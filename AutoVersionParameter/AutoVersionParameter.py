import adsk.core
import adsk.fusion
import traceback

handlers = []

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
    except:
        pass

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
    except:
        pass

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

            existing_param_value = None
            design = adsk.fusion.Design.cast(
                doc.products.itemByProductType('DesignProductType')
            )
            if design:
                for p in design.userParameters:
                    if p.name == 'version_num':
                        try:
                            existing_param_value = int(float(p.expression))
                        except:
                            existing_param_value = None
                        break
            
            # Determine target version: the version that will exist after this save completes
            # For new files (version 0), the first save creates version 1
            # For existing files, increment by 1
            if doc.dataFile:
                current_version = doc.dataFile.versionNumber
                if current_version <= 1 and existing_param_value == 0:
                    target_version = 1
                elif current_version < 1:
                    target_version = 1
                else:
                    target_version = current_version + 1
            else:
                target_version = 1

            update_version_before_save(doc, target_version)
        except:
            pass

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
    except:
        pass