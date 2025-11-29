from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from knowledge_graph.validator.rdf_validator import RDFValidator

router = APIRouter(
    prefix="/validator",
    tags=["RDF Validator"]
)
@router.post("/validate")
async def validate_rdf():
    """
    Validate all RDF TTL files automatically from the instances directory.
    """
    try:
        validator = RDFValidator()
        validator.load_ttl_files()
        results = validator.run_shacl_validation()
        validator.generate_report(results)

        # Only return JSON-serializable fields
        serializable_results = {
            fname: {
                "conforms": r["conforms"],
                "triple_count": r["triple_count"],
                "report_text": r["report_text"]
            }
            for fname, r in results.items()
        }

        return JSONResponse(content=serializable_results)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
