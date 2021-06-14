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

        self._logger.debug("TEST API The test button was pressed...")
        self._logger.debug(f"request = {request}")

        title = "This is the message title"  # text only, no special characters
        description = "this is the body of the message or email"
        printer_name = (
            self._identifier  # you can use this to inform people this is coming from your plugin
        )
        thumbnail_filename = (
            self._basefolder + "/static/img/Alert.png"
        )  # path to a thumbnail image to be sent. Set to None if not used.
        # thumbnail_filename = None
        do_cam_snapshot = (
            True  # True tries to send an image from the webcam if enabled in OctoText
            # only one image is sent, either the thumbnail or webcam and the
            # thumbnail takes precedence
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

        # using the helper function to call OctoText. send_text assigned in on_after_startup()
        if self.send_text:
            result = self.send_text(command="OctoText", data={"test": data})
            self._logger.debug(f"OctoText api result {result}")
            return flask.make_response(flask.jsonify(result=True, error=result))

        # the following code sends the message through the PluginManager and is less efficient than using the helper
        # above. As written this code will never execute as OctoText has a helper function and it is the preferred way
        # to access the plugin.
        # It does work however, and it is left here because the code functions and may be helpful in some cases.

        # check to see if OctoText exists
        p_info = self._plugin_manager.get_plugin_info("OctoText", require_enabled=True)
        if p_info is None:
            self._logger.debug("OctoText is not loaded or enabled on this system!")
            error = "NOT_LOADED"
            return flask.make_response(flask.jsonify(result=True, error=error))
        self._logger.debug(f"OctoText version {p_info.version}")
        self._logger.debug(f"OctoText info block: {p_info}")
        if p_info.loaded:
            self._logger.debug("OctoText has been loaded")
        error = None
        try:
            self._plugin_manager.send_plugin_message("OctoText", {"test": data})
        except Exception as e:
            error = "NOT_ENABLED"
            self._logger.debug(f"Exception sending API message: {e}")
        return flask.make_response(flask.jsonify(result=True, error=error))

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
        if helpers and "send_text" in helpers:
            self.send_text = helpers["send_text"]

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
