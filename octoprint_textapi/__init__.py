# -*- coding: utf-8 -*-
from email.message import EmailMessage
from email.utils import formatdate

import flask
import octoprint.plugin

# The purpose of this plugin is to demonstrate how to format notifications, detect the presence of OctoText, look for
# error responses and send text notifications in your plugin.
# It requires OctoText version > 0.3.1


class TextapiPlugin(
    octoprint.plugin.SettingsPlugin,
    octoprint.plugin.StartupPlugin,
    octoprint.plugin.AssetPlugin,
    octoprint.plugin.SimpleApiPlugin,
    octoprint.plugin.TemplatePlugin,
):

    ##~~ SettingsPlugin mixin

    def get_settings_defaults(self):
        return {
            "push_message": None,
            "show_navbar_button": True,
        }

    ##~~ AssetPlugin mixin

    def get_assets(self):
        # Define your plugin's asset files to automatically include in the
        # core UI here.
        return {
            "js": ["js/textapi.js"],
        }

    # for this test a button is included in the nav bar that initiates the sending of the message (empty mailbox)
    def on_api_get(self, request):
        """
        Format an EmailMessage to send to OctoText
        """

        self._logger.debug("TEST API The test button was pressed...")
        self._logger.debug(f"request = {request}")

        backupFileLocation = (
            self._basefolder + "/static/img/Alert.zip"
        )  # path to an image or file to be sent. Set to None if not used.

        emailMessage = EmailMessage()
        emailMessage["Subject"] = "Test from API"
        # changing the From or To settings in an email message will override the Octotext settings
        # this may or may not work depending on your mail provider. Leaving these fields blank
        # uses the user settings in Octotext
        # emailMessage["From"] = "OctoText@outlook.com"  # 'OctoText@outlook.com'
        # emailMessage["To"] = "ollisgit+octotext@gmail.com"
        emailMessage["Date"] = formatdate(localtime=True)
        emailMessage.set_content("This is my body message", charset="utf-8")

        fp = open(backupFileLocation, "rb")
        emailMessage.add_attachment(
            fp.read(),
            maintype="application",
            subtype="zip",
            filename="myBackupFilename.zip",
        )

        # send the email using OctoText
        self.send_email(command="OctoText", data=emailMessage)
        return flask.make_response(flask.jsonify(result=True, error=None))

        # check to see if OctoText exists
        # p_info = self._plugin_manager.get_plugin_info("OctoText", require_enabled=True)
        # if p_info is None:
        #     self._logger.debug("OctoText is not loaded or enabled on this system!")
        #     error = "NOT_LOADED"
        #     return flask.make_response(flask.jsonify(result=True, error=error))
        # self._logger.debug(f"OctoText version {p_info.version}")
        # self._logger.debug(f"OctoText info block: {p_info}")
        # if p_info.loaded:
        #     self._logger.debug("OctoText has been loaded")
        # error = None

        # try:
        #     self._plugin_manager.send_plugin_message("OctoText", {"test": data})
        # except Exception as e:
        #     error = "NOT_ENABLED"
        #     self._logger.debug(f"Exception sending API message: {e}")
        # return flask.make_response(flask.jsonify(result=True, error=error))

    sent_text = ""

    def on_after_startup(self):
        # just let the user know that the plugin has loaded
        basefolder = self._basefolder
        self._logger.info(f"plugin base folder: {basefolder}")
        self._logger.info("*** Test API for OctoText loaded!!! ***")

        # find the helper function for OctoText - send_text:
        # def send_text(self,
        #              command: {__ne__},
        #              data: {__getitem__},
        #              permissions: Any = None) -> Optional[bool]
        helpers = self._plugin_manager.get_helpers("OctoText")
        if helpers and "send_email" in helpers:
            self.send_email = helpers["send_email"]

    ##~~ Softwareupdate hook

    def get_update_information(self):
        # Define the configuration for your plugin to use with the Software Update
        # Plugin here. See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
        # for details.
        return {
            "textapi": {
                "displayName": "Textapi Plugin",
                "displayVersion": self._plugin_version,
                "type": "github_release",
                "user": "berrystephenw",
                "repo": "OctoPrint-Textapi",
                "current": self._plugin_version,
                "pip": "https://github.com/berrystephenw/OctoPrint-Textapi/archive/{target_version}.zip",
            }
        }


__plugin_name__ = "Textapi Plugin"
__plugin_pythoncompat__ = ">=3,<4"  # only python 3


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = TextapiPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
