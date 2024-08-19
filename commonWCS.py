()-->cat partialData.py
import time
AdminApp.update('WC_prod01', 'file', '[-operation addupdate -contents /usr/opt/app/IBM/WebSphere/AppServer/source/WebSphereCommerceServerExtensionsData.jar -contenturi WebSphereCommerceServerExtensionsData.jar]')
AdminConfig.save()
()-->cat partialLogic.py
import time
AdminApp.update('WC_prod01', 'file', '[-operation addupdate -contents /usr/opt/app/IBM/WebSphere/AppServer/source/WebSphereCommerceServerExtensionsLogic.jar -contenturi WebSphereCommerceServerExtensionsLogic.jar]')
AdminConfig.save()
()-->cat partialApp.py
import time
AdminApp.update('WC_test01', 'partialapp', '[-contents /usr/opt/app/IBM/WebSphere/AppServer/source/partialApp.zip]')
AdminConfig.save()