import re
import httpx
from typing import Any, Dict
from tools.base import ScientificTool

_VARIATION_API = "https://api.ncbi.nlm.nih.gov/variation/v0"
_EUTILS_API = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

class DbSNPTool(ScientificTool):
    """Query NCBI dbSNP via the Variation Services API and E-utilities.

    Supports:
    - rsID lookup (rs7412, rs268 …)
    - Gene/keyword text search → top rsIDs
    - Genomic coordinate resolution (chr pos ref alt)
    """

    @property
    def name(self) -> str:
        return "dbSNP Variant Search"

    @property
    def description(self) -> str:
        return (
            "Search NCBI dbSNP for short genetic variants (SNPs/indels). "
            "Resolves rsIDs to variant type, gene associations, clinical significance, "
            "allele frequencies, and GRCh38 coordinates. "
            "Also accepts gene names or free-text queries."
        )

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    async def execute(self, query: str, max_results: int = 5, **kwargs) -> Dict[str, Any]:
        """Route the query to the appropriate sub-method."""
        query = query.strip()

        # Detect rsID pattern (rs followed by digits, optional leading whitespace)
        rsid_match = re.fullmatch(r"rs?(\d+)", query, re.IGNORECASE)
        if rsid_match:
            return await self._get_by_rsid(rsid_match.group(1))

        # Detect VCF-style coordinate: "chr pos ref alt"  e.g. "8 19962213 C T"
        vcf_match = re.fullmatch(
            r"(?:chr)?(\w+)\s+(\d+)\s+([ACGT]+)\s+([ACGT]+)", query, re.IGNORECASE
        )
        if vcf_match:
            chrom, pos, ref, alt = vcf_match.groups()
            return await self._resolve_coordinates(chrom, pos, ref, alt)

        # Default: free-text / gene-name search via E-utilities
        return await self._search_text(query, max_results)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    async def _get_by_rsid(self, rsid_num: str) -> Dict[str, Any]:
        """Fetch and abbreviate a RefSNP record for a single rsID."""
        url = f"{_VARIATION_API}/refsnp/{rsid_num}"
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(url)
                if resp.status_code == 404:
                    return {"status": "not_found", "message": f"rs{rsid_num} not found in dbSNP."}
                resp.raise_for_status()
                data = resp.json()
                return {
                    "status": "success",
                    "query": f"rs{rsid_num}",
                    "results": [self._abbreviate_refsnp(data)],
                    "metadata": {"source": "dbSNP", "api": "NCBI Variation Services"}
                }
        except httpx.RequestError as e:
            return {"status": "error", "message": f"Failed to reach dbSNP API: {e}"}

    async def _resolve_coordinates(
        self, chrom: str, pos: str, ref: str, alt: str
    ) -> Dict[str, Any]:
        """Resolve VCF-style genomic coordinates to an rsID (GRCh38)."""
        # GRCh38 accession: GCF_000001405.40
        url = (
            f"{_VARIATION_API}/vcf/{chrom}/{pos}/{ref}/{alt}/contextuals"
            f"?assembly=GCF_000001405.40"
        )
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(url)
                if resp.status_code == 404:
                    return {
                        "status": "not_found",
                        "message": f"No dbSNP entry for {chrom}:{pos} {ref}>{alt} (GRCh38)."
                    }
                resp.raise_for_status()
                data = resp.json()
                items = data.get("data", {}).get("items", [])
                if not items:
                    return {"status": "not_found", "message": "No matching variants found."}
                rsids = [f"rs{item['refsnp_id']}" for item in items if "refsnp_id" in item]
                return {
                    "status": "success",
                    "query": f"{chrom}:{pos} {ref}>{alt}",
                    "resolved_rsids": rsids,
                    "metadata": {"source": "dbSNP", "assembly": "GRCh38"}
                }
        except httpx.RequestError as e:
            return {"status": "error", "message": f"Failed to reach dbSNP API: {e}"}

    async def _search_text(self, query: str, max_results: int) -> Dict[str, Any]:
        """Search dbSNP by gene name or keyword, return top variant summaries."""
        search_url = f"{_EUTILS_API}/esearch.fcgi"
        summary_url = f"{_EUTILS_API}/esummary.fcgi"

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                # Step 1: search for rsIDs
                search_resp = await client.get(search_url, params={
                    "db": "snp",
                    "term": query,
                    "retmode": "json",
                    "retmax": max_results,
                    "sort": "clinical_significance"
                })
                search_resp.raise_for_status()
                id_list = search_resp.json().get("esearchresult", {}).get("idlist", [])

                if not id_list:
                    return {
                        "status": "success",
                        "query": query,
                        "results": [],
                        "message": "No variants found in dbSNP for this query."
                    }

                # Step 2: fetch summaries
                summary_resp = await client.get(summary_url, params={
                    "db": "snp",
                    "id": ",".join(id_list),
                    "retmode": "json"
                })
                summary_resp.raise_for_status()
                summary_data = summary_resp.json()

                results = []
                for uid in summary_data.get("result", {}).get("uids", []):
                    doc = summary_data["result"][uid]
                    results.append({
                        "rsid": f"rs{doc.get('snp_id', uid)}",
                        "gene": doc.get("genes", [{}])[0].get("name") if doc.get("genes") else None,
                        "variant_class": doc.get("snp_class"),
                        "clinical_significance": doc.get("clinical_significance"),
                        "allele_origin": doc.get("allele_origin"),
                        "chromosome": doc.get("chr"),
                        "position_grch38": doc.get("chrpos_prev_assm"),
                    })

                return {
                    "status": "success",
                    "query": query,
                    "results": results,
                    "metadata": {
                        "count": len(results),
                        "source": "dbSNP",
                        "api": "NCBI E-utilities"
                    }
                }
        except httpx.RequestError as e:
            return {"status": "error", "message": f"Failed to reach NCBI E-utilities: {e}"}

    # ------------------------------------------------------------------
    # Record abbreviation (mirrors dbsnp_cli.py logic)
    # ------------------------------------------------------------------

    def _abbreviate_refsnp(self, record: dict) -> dict:
        """Extract the most useful fields from a raw RefSNP record."""
        snapshot = record.get("primary_snapshot_data", {})
        rsid = f"rs{record.get('refsnp_id', '?')}"

        # Variant type & alleles
        allele_annotations = snapshot.get("allele_annotations", [])
        freq_data = []
        for ann in allele_annotations:
            for freq in ann.get("frequency", []):
                freq_data.append({
                    "study": freq.get("study_name"),
                    "allele": freq.get("observation", {}).get("inserted_sequence"),
                    "frequency": freq.get("allele_count", 0) / max(freq.get("total_count", 1), 1)
                })

        # Clinical significance
        clinical_sigs = []
        for ann in allele_annotations:
            for clin in ann.get("clinical", []):
                for sig in clin.get("clinical_significances", []):
                    clinical_sigs.append(sig)

        # Gene associations
        support_assemblies = snapshot.get("support_assemblies", [])
        genes = []
        for asm in support_assemblies:
            for gene in asm.get("genes", []):
                name = gene.get("locus")
                if name and name not in genes:
                    genes.append(name)

        # Genomic placement (GRCh38)
        placement_grch38 = None
        for p in snapshot.get("placements_with_allele", []):
            if not p.get("is_ptlp"):
                continue
            for trait in p.get("placement_annot", {}).get("seq_id_traits_by_assembly", []):
                if trait.get("assembly_accession") == "GCF_000001405.40":
                    alleles = p.get("alleles", [])
                    for a in alleles:
                        sp = a.get("allele", {}).get("spdi", {})
                        if sp:
                            placement_grch38 = {
                                "seq_id": sp.get("seq_id"),
                                "position": sp.get("position"),
                                "deleted_sequence": sp.get("deleted_sequence"),
                                "inserted_sequence": sp.get("inserted_sequence"),
                            }
                            break

        return {
            "rsid": rsid,
            "variant_type": snapshot.get("variant_type"),
            "genes": genes,
            "clinical_significance": list(set(clinical_sigs)) if clinical_sigs else ["Unknown"],
            "allele_frequencies": freq_data[:5],  # top 5 entries
            "placement_grch38": placement_grch38,
        }
