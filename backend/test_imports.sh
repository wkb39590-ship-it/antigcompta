#!/bin/bash
python -c "
import sys
try:
    print('Testing imports...')
    from routes.auth import router
    from routes.admin import router as admin_router
    print('✅ All imports successful')
except Exception as e:
    print(f'❌ Import Error: {str(e)}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
"
