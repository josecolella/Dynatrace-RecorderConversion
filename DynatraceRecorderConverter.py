# -*- coding: utf-8 -*-
# Author: Jose Miguel Colella
# email: jose.colella@dynatrace.com
import base64
import json
import itertools
from lxml import etree


class DynatraceRecorderConverter(object):

    """This class also for the conversion between the two
    output formats generated by the Dynatrace Recorder; json and gsl.
    """

    @staticmethod
    def convertJSONFileToGSLFile(jsonFile, gslFile="tmp"):
        """Converts the contents of the json file to a gsl file

        Args:
            jsonFile (str): The name of the json file to read
            gslFile (str): The name of the gsl file to generate

        Returns:
            NoneType: writes the gsl file provided the ``gslFile`` parameter
        """
        jsonConverter = _JSONConverter(jsonFile)
        jsonConverter.convert()
        jsonConverter.writeFile(gslFile)

    @staticmethod
    def convertGslFileToJSONFile(gslFile, jsonFile):
        """
        TODO
        """
        pass


class _JSONConverter(object):

    """A ulility class used to do the conversion of a Dynatrace
    Recorder json file to an appropriate gsl file

    Attributes:
        rootNode (lxml.etree._Element): The root node of the gsl document
    """

    def __init__(self, jsonFile):
        """Initializes the converter with the contents of the
        json file.

        Args:
            json (str): The name of the json file
        """

        with open(jsonFile) as f:
            self.jsonContents = json.load(f)
        self.rootNode = None

    def convert(self):
        # Create the gsl root element
        self.rootNode = etree.Element(
            "Transaction",
            doObjectDownloads="true",
            doPageSummary="false",
            name=self.jsonContents["name"]
        )
        # Method for adding user agent info if in json script
        self._createUserAgentSection()
        # Method for creating the configuration parameters section
        self._createConfigurationSection()
        # Method for creating the steps section
        self._createStepSection()
        # Add pre_script attr to first node
        self._addPreScriptAttribute()

    def _createUserAgentSection(self):

        if self.jsonContents.get("userAgent") is not None:
            headerString = "http://www.gomez.com/headers"
            # Create configuration node
            configurationNode = etree.Element(
                "Configuration", name=headerString)
            # Create Param node
            parameter = etree.Element(
                "Param", name="User-Agent", value="{}".format(self.jsonContents["userAgent"]))
            # Append Param node to configuration node
            configurationNode.append(parameter)
            # Append Configuration node to root Transaction node
            self.rootNode.append(configurationNode)

    def _createDeadlineNodesIter(self):
        deadlineNodes = ()
        deadline = {
            "hardDeadline": "http://www.gomez.com/settings/hard_deadline",
            "softDeadline": "http://www.gomez.com/settings/soft_deadline"
        }
        deadlineNodes = (etree.Element("Param", name="{}".format(pvalue), value="{}".format(self.jsonContents[key]))
                         for key, pvalue in deadline.items() if self.jsonContents.get(key) is not None)
        return deadlineNodes

    def _createConfigurationSection(self):
        """Creates and appends all the test configuration and creates all
        the appropriate xml nodes
        """
        # Creates the <Configuration> xml element
        configurationNode = etree.SubElement(self.rootNode, "Configuration")
        # The configuration dictionary including flash and Scoe settings
        configDict = {
            "enableFlash": "http://www.gomez.com/capabilities/enable_flash",
            "enableScoe": "http://www.gomez.com/capabilities/enable_scoe",
        }
        # Network settings
        networkSettings = {"ipMode": "http://www.gomez.com/settings/ip_mode"}
        # Creates the <Param> tags for the enableFlash and enableScoe
        capabilities = (etree.Element("Param", name="{}".format(pvalue), value="")
                        for key, pvalue in configDict.items() if self.jsonContents.get(key) is not None)
        # Creates the <Param> tag for the network settings
        network = (etree.Element("Param", name="{}".format(pvalue), value="{}".format(
            self.jsonContents[key])) for key, pvalue in networkSettings.items())
        # Creates the <Param> tags for the GSL and browser version
        settings = (etree.Element("Param", name="{}".format(configuration["name"]), value="{}".format(
            configuration["value"])) for configuration in self.jsonContents["configurations"])
        # Create an iterator with all the <Param> tags
        parameterIterator = itertools.chain(
            capabilities, self._createDeadlineNodesIter(), network, settings)
        # Append the tags to the root node
        for parameter in parameterIterator:
            configurationNode.append(parameter)

    def _createSubstitutionNodesIter(self, step):
        # Given a step returns a Substitution node list
        substitutionNodes = None

        if step.get("substitutions") is not None:

            substitutionNodes = (etree.Element("Substitution",
                                               selector="{}".format(
                                                   substitution["selector"]),
                                               token="{}".format(
                                                   substitution["token"]),
                                               value="{}".format(substitution["value"]))
                                 for substitution in step["substitutions"])
        return substitutionNodes

    def _createStepSection(self):
        """Creates and appends all the test steps into the definition of the gsl
        document
        """
        for step in self.jsonContents["steps"]:
            jsonEncodedAction = json.dumps(
                step["actions"]).encode("utf8")
            postScript = base64.b64encode(jsonEncodedAction)
            pageRequestNode = etree.Element("PageRequest",
                                            displayName="{}".format(
                                                step["description"]),
                                            method="GET",
                                            post_script="{}".format(
                                                postScript.decode("utf-8")),
                                            url=step["url"]
                                            )

            if step.get("softDeadline") or step.get("hardDeadline"):
                configurationNode = etree.Element("Configuration")
                for deadlineNode in self._createDeadlineNodesIter():
                    configurationNode.append(deadlineNode)
                pageRequestNode.append(configurationNode)
            substitutionNodes = self._createSubstitutionNodesIter(step)
            if substitutionNodes is not None:
                for substititutionNode in substitutionNodes:
                    pageRequestNode.append(substititutionNode)
            self.rootNode.append(pageRequestNode)

    def _addPreScriptAttribute(self):
        """Adds the pre_script attribute to the first test step which defines
        the client certifications
        """
        preScriptDict = {
            "script": {"clientCerts": self.jsonContents["clientCerts"]}}
        preScriptEnc = base64.b64encode(
            json.dumps(preScriptDict, indent=4).encode("utf-8"))
        # Add the pre-script to the first <PageRequest> node
        self.rootNode[1].attrib["pre_script"] = preScriptEnc.decode("utf-8")

    def writeFile(self, gslFileName="tmp"):
        """Writes the gsl file that has been created by converting the
        json content

        Args:
            gslFileName (str[Optional]): Name of the gsl file to write.
                If name is not provided, 'tmp' is used and saved to
                the current directory
        """
        with open("{}.gsl".format(gslFileName), "w") as gslFile:
            gslContents = (
                etree.tostring(self.rootNode, pretty_print=True)).decode("utf8")
            gslFile.write(gslContents)
