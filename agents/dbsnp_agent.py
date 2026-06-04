from typing import Dict, Any
from agents.base import BaseAgent
from tools.variant.dbsnp_tool import DbSNPTool


class DbSNPAgent(BaseAgent):
    """Specialized agent for querying NCBI dbSNP.

    Handles:
    - rsID lookups (variant type, gene, clinical significance, allele frequencies)
    - Gene/keyword searches returning top variant summaries
    - Genomic coordinate → rsID resolution (VCF format: chr pos ref alt)
    """

    def __init__(self):
        super().__init__(
            name="DbSNPAgent",
            description=(
                "Searches NCBI dbSNP for short genetic variants (SNPs/indels). "
                "Accepts rsIDs (e.g. rs7412), gene names, free-text queries, or "
                "VCF-format coordinates (chr pos ref alt). Returns variant type, "
                "gene associations, clinical significance, allele frequencies, "
                "and GRCh38 genomic coordinates."
            )
        )
        self.register_tool(DbSNPTool())

    async def process_task(self, task_query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        print(f"   -> [DbSNPAgent] Querying dbSNP for: '{task_query}'")
        if not self.tools:
            return {"error": "No tools registered"}

        tool = self.tools[0]
        result = await tool.execute(task_query, max_results=5)
        return result
