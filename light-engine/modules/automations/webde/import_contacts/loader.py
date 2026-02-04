from .desktop.run import ImportContacts as DesktopImportContacts
import os

def run(account, job_id=None, **kwargs):
    """
    Selects the right platform (desktop/mobile) and runs the automation.
    """
    automation_class = DesktopImportContacts
    
    vcf_file_path = kwargs.get("vcf_file")

    if vcf_file_path and not os.path.exists(vcf_file_path) and vcf_file_path.startswith("data:"):
        try:
            import base64
            import tempfile
            
            header, encoded = vcf_file_path.split(",", 1)
            data = base64.b64decode(encoded)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".vcf", mode='wb') as tmp:
                tmp.write(data)
                vcf_file_path = tmp.name
        except Exception as e:
            print(f"Failed to decode base64 file: {e}")

    log_dir = kwargs.get("log_dir")

    automation = automation_class(
        account=account,
        user_agent_type="desktop",
        vcf_file_path=vcf_file_path,
        job_id=job_id,
        log_dir=log_dir
    )

    return automation.execute()