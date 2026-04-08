from fastapi import APIRouter
from .endpoints import apps, scan, monitoring, threats, incidents, reports, permissions, analysis, network
from .endpoints import advanced

router = APIRouter()

router.include_router(apps.router, prefix="/apps", tags=["Apps"])
router.include_router(scan.router, prefix="/scan", tags=["Scanning"])
router.include_router(monitoring.router, prefix="/monitor", tags=["Monitoring"])
router.include_router(threats.router, prefix="/threats", tags=["Threat Intelligence"])
router.include_router(incidents.router, prefix="/incidents", tags=["Incidents"])
router.include_router(reports.router, prefix="/reports", tags=["Reports"])
router.include_router(permissions.router, prefix="/permissions", tags=["Permissions"])
router.include_router(analysis.router, prefix="/analysis", tags=["Analysis"])
router.include_router(network.router, prefix="/network", tags=["Network"])
router.include_router(advanced.router, prefix="/advanced", tags=["Advanced Features"])
