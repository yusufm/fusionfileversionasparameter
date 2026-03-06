import adsk.core
import adsk.fusion
import traceback

handlers = []


def log_error(context):
    app = adsk.core.Application.get()
    if app:
        app.log('[AutoVersionParameter] {}: {}'.format(context, traceback.format_exc()))

def update_version_before_save(doc, target_version):
    """
    Update version_num parameter before save, with timeline suppression.
    """
    design = adsk.fusion.Design.cast(
        doc.products.itemByProductType('DesignProductType')
    )
    if not design:
        return

    params = design.userParameters
    desired_expr = str(target_version)
    
    # Find or create the parameter
    version_num_param = None
    for p in params:
        if p.name == 'version_num':
            version_num_param = p
            break
    
    # Start a timeline group to suppress undo
    timeline = design.timeline
    if timeline:
        timeline_marker = timeline.markerPosition
    
    try:
        if not version_num_param:
            params.add(
                'version_num',
                adsk.core.ValueInput.createByString(desired_expr),
                '',
                'Numeric version for automation'
            )
        elif version_num_param.expression != desired_expr:
            version_num_param.expression = desired_expr
        
        # Roll back timeline to before our change to hide it from undo
        if timeline and timeline_marker >= 0:
            timeline.markerPosition = timeline_marker
    except Exception:
        log_error('update_version_before_save')

def ensure_version_param(doc):
    """Helper to create version_num parameter if it doesn't exist"""
    try:
        design = adsk.fusion.Design.cast(
            doc.products.itemByProductType('DesignProductType')
        )
        if not design:
            return
        
        params = design.userParameters
        
        version = 0
        
        # Check if parameter already exists
        for p in params:
            if p.name == 'version_num':
                return
        
        # Create parameter with version 0 for new files, or current version for existing
        if doc.dataFile:
            version = doc.dataFile.versionNumber

        params.add(
            'version_num',
            adsk.core.ValueInput.createByString(str(version)),
            '',
            'Numeric version for automation'
        )
    except Exception:
        log_error('ensure_version_param')


def get_existing_version_param_value(doc):
    """Read the current integer value of version_num if present."""
    design = adsk.fusion.Design.cast(
        doc.products.itemByProductType('DesignProductType')
    )
    if not design:
        return None

    for p in design.userParameters:
        if p.name == 'version_num':
            try:
                return int(float(p.expression))
            except Exception:
                return None

    return None


def get_target_version(doc, existing_param_value):
    """
    Determine the version number the document should store during save.

    Fusion's Save As flow can create a new v1 data file while carrying over the
    source design's version_num parameter. When that happens, keep the copied
    file at v1 instead of incorrectly jumping to v2.
    """
    if not doc.dataFile:
        return 1

    current_version = doc.dataFile.versionNumber
    if current_version < 1:
        return 1

    if current_version == 1 and existing_param_value not in (None, 0, 1):
        return 1

    if existing_param_value == 0:
        return 1

    return current_version + 1

class DocumentActivatedHandler(adsk.core.DocumentEventHandler):
    """Handles documentActivated event - initializes parameter for existing files without it"""
    def notify(self, args):
        ensure_version_param(args.document)

class DocumentSavingHandler(adsk.core.DocumentEventHandler):
    """Handles documentSaving event - updates parameter before save"""
    def notify(self, args):
        try:
            doc = args.document
            if not doc:
                return

            ensure_version_param(doc)
            existing_param_value = get_existing_version_param_value(doc)
            target_version = get_target_version(doc, existing_param_value)
            update_version_before_save(doc, target_version)
        except Exception:
            log_error('DocumentSavingHandler.notify')

def run(context):
    """Called when Add-In is run"""
    app = adsk.core.Application.get()
    
    # Register activated handler - initializes param for existing files without it
    activated_handler = DocumentActivatedHandler()
    app.documentActivated.add(activated_handler)
    handlers.append(activated_handler)
    
    # Register saving handler - updates param before save with timeline suppression
    saving_handler = DocumentSavingHandler()
    app.documentSaving.add(saving_handler)
    handlers.append(saving_handler)

def stop(context):
    """Called when Add-In is stopped"""
    try:
        app = adsk.core.Application.get()
        
        if app.documentActivated:
            for handler in handlers:
                if isinstance(handler, DocumentActivatedHandler):
                    app.documentActivated.remove(handler)
        
        if app.documentSaving:
            for handler in handlers:
                if isinstance(handler, DocumentSavingHandler):
                    app.documentSaving.remove(handler)
        
        handlers.clear()
    except Exception:
        log_error('stop')
