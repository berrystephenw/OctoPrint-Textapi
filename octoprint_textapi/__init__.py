# -*- coding: utf-8 -*-
from __future__ import absolute_import

import flask
import octoprint.plugin

# The purpose of this plugin is to demonstrate how to format notifications, detect the presence of OctoText, look for
# error responses and send text notifications in your plugin.
# It requires OctoText version > 0.3.0


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

        self._logger.debug("TEST API The test button was pressed...")
        self._logger.debug(f"request = {request}")

        title = "This is the message title"
        description = "this is the body of the message or email"
        printer_name = (
            self._identifier  # you can use this to inform people this is coming from your plugin
        )
        thumbnail_filename = ""  # path to a thumbnail image to be sent.
        do_cam_snapshot = (
            True  # True tries to send an image from the webcam if enabled in OctoText
        )
        data = dict(
            [
                ("title", title),
                ("description", description),
                ("sender", printer_name),
                ("thumbnail", thumbnail_filename),
                ("send_image", do_cam_snapshot),
            ]
        )
        error = None
        try:
            self._plugin_manager.send_plugin_message("OctoText", {"test": data})
        except Exception as e:
            error = "NOT_LOADED"
            self._logger.debug(f"Exception sending API message: {e}")
        return flask.make_response(flask.jsonify(result=True, error=error))

    def on_after_startup(self):
        # just let the user know that the plugin has loaded
        self._logger.info("*** Test API for OctoText loaded!!! ***")

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
