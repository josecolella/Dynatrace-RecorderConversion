import base64
import json
import lxml


class DynatraceRecorder(object):

    """docstring for DyantraceRecorder"""

    def __init__(self, arg):
        pass

    def convertJSONFileToGSLFile(jsonFile, gslFile):
        jsonContents = json.load(jsonFile)
        return jsonContents

    def convertJSONtoGSL(jsonString, gslString):
        pass

    def _setClientCerts(jsonContents):
        pass

class GSLFile(object):

    """docstring for GSLFile"""

    def __init__(self, jsonContents):
"""
<Transaction doObjectDownloads="true" doPageSummary="false" name="{scriptName}">
    <Configuration>
        <Param name="http://www.gomez.com/capabilities/enable_flash" value=""/>
        <Param name="http://www.gomez.com/settings/ip_mode" value="{scriptNetwork}"/>
        <Param name="http://www.gomez.com/settings/gsl_version" value="2"/>
        <Param name="http://www.gomez.com/settings/browser_version" value="IE7"/>
    </Configuration>
    <PageRequest displayName="Hacker News" method="GET" post_script="{stepDetail}" pre_script="{}" url="https://news.ycombinator.com/"/>
</Transaction
""".format(scriptName=jsonContents["name"], scriptNetwork=jsonContents["ipMode"], stepDetail=base64.b64encode(jsonContents[""]))
