import adsk.core
import adsk.fusion
import traceback

handlers = []

def update_version_num(doc):
    """
    Create or update a numeric 'version_num' parameter.
    """
    if not doc or not doc.dataFile:
        return

    version_number = doc.dataFile.versionNumber

    design = adsk.fusion.Design.cast(
        doc.products.itemByProductType('DesignProductType')
    )
    if not design:
        return

    params = design.userParameters

    # Check if 'version_num' exists
    version_num_param = None
    for p in params:
        if p.name == 'version_num':
            version_num_param = p
            break

    # Try updating existing parameter; delete/recreate if corrupted
    if version_num_param:
        try:
            version_num_param.expression = str(version_number)
            return
        except:
            version_num_param.deleteMe()
            version_num_param = None

    # Create fresh numeric parameter
    params.add(
        'version_num',
        adsk.core.ValueInput.createByString(str(version_number)),
        '',  # unitless numeric
        'Numeric version for automation'
    )

class DocumentActivatedHandler(adsk.core.DocumentEventHandler):
    """Handles documentActivated event"""
    def notify(self, args):
        try:
            update_version_num(args.document)
        except:
            adsk.core.Application.get().userInterface.messageBox(
                'AutoVersionParameter error:\n' + traceback.format_exc()
            )

def run(context):
    """Called when Add-In is run"""
    app = adsk.core.Application.get()
    handler = DocumentActivatedHandler()
    app.documentActivated.add(handler)
    handlers.append(handler)

def stop(context):
    """Called when Add-In is stopped"""
    pass