from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.core.driver_context import InitCommandContext, ResourceCommandContext, AutoLoadResource,  AutoLoadAttribute, AutoLoadDetails
from cloudshell.api.cloudshell_api import CloudShellAPISession
import requests
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import json
import inject


class Ixia52XxDriver (ResourceDriverInterface):

    def cleanup(self):
        """
        Destroy the driver session, this function is called everytime a driver instance is destroyed
        This is a good place to close any open sessions, finish writing to log files
        """
        pass

    def __init__(self):
        """
        ctor must be without arguments, it is created with reflection at run time
        """
        pass

    def initialize(self, context):
        """
        Initialize the driver session, this function is called everytime a new instance of the driver is created
        This is a good place to load and cache the driver configuration, initiate sessions etc.
        :param InitCommandContext context: the context the command runs on
        """
        pass


    # The ApplyConnectivityChanges function is intended to be used for using switches as connectivity providers
    # for other devices. If the Switch shell is intended to be used a DUT only there is no need to implement it

    def ApplyConnectivityChanges(self, context, request):
        """
        Configures VLANs on multiple ports or port-channels
        :param ResourceCommandContext context: The context object for the command with resource and reservation info
        :param str request: A JSON object with the list of requested connectivity changes
        :return: a json object with the list of connectivity changes which were carried out by the switch
        :rtype: str
        """
        """
        :type context: drivercontext.ResourceCommandContext
        :type json: str
        """
        session = CloudShellAPISession(host=context.connectivity.server_address,
                                       token_id=context.connectivity.admin_auth_token,
                                       domain="Global")

        requestJson = json.loads(request)


        #Build Response
        response = {"driverResponse":{"actionResults":[]}}


        for actionResult in requestJson['driverRequest']['actions']:
            actionResultTemplate = {"actionId":None, "type":None, "infoMessage":"", "errorMessage":"", "success":"True", "updatedInterface":"None"}
            actionResultTemplate['type'] = str(actionResult['type'])
            actionResultTemplate['actionId'] = str(actionResult['actionId'])
            response["driverResponse"]["actionResults"].append(actionResultTemplate)



        return 'command_json_result=' + str(response) + '=command_json_result_end'

        pass



    def get_inventory(self, context):
        """
        Discovers the resource structure and attributes.
        :param AutoLoadCommandContext context: the context the command runs on
        :return Attribute and sub-resource information for the Shell resource
        :rtype: AutoLoadDetails
        """

        session = CloudShellAPISession(host=context.connectivity.server_address,
                                       token_id=context.connectivity.admin_auth_token,
                                       domain="Global")

        pw = session.DecryptPassword(context.resource.attributes['Password']).Value

        un = context.resource.attributes["User"]
        ip = context.resource.address
        port = str(context.resource.attributes["API Port"])
        prefix = str(context.resource.attributes["API Access"])

        url = prefix+"://"+ip+":"+port+"/api"

        sub_resources = []
        attributes = [AutoLoadAttribute('', 'Model', 'Ixia 58xx'),AutoLoadAttribute('', 'Vendor', 'Ixia')]


        # get all ports
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        portsRequest = requests.get(url+'/ports', auth=HTTPBasicAuth(un,pw), verify=False)
        portsObj = json.loads(portsRequest.text)
        # loop thru each port and learn more
        for port in portsObj:
            portRequest = requests.get(url+'/ports/'+str(port['id']), auth=HTTPBasicAuth(un,pw), verify=False)
            portObj = json.loads(portRequest.text)
            sub_resources.append(AutoLoadResource(model='NTO Port', name=portObj['default_name'], relative_address=str(port['id'])))
            attributes.append(AutoLoadAttribute(str(port['id']), 'Port Speed', portObj['media_type']))
            attributes.append(AutoLoadAttribute(str(port['id']), 'Serial Number', portObj['uuid']))
            attributes.append(AutoLoadAttribute(str(port['id']), 'Port Description', str(portObj['name']) + " " + str(portObj['description'])))


        return AutoLoadDetails(sub_resources,attributes)

        pass
