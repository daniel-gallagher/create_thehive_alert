# thehive_create_alert alert settings

action.thehive_create_alert = [0|1]
* Enable thehive_create_case notification

action.thehive_create_alert.param.caseTemplate = <string>
* The case template to use for imported alerts.
* Defaults to "default"
* (required)

action.thehive_create_alert.param.type = <string>
* Alert type. Defaults to "alert"
* (required)

action.thehive_create_alert.param.source = <string>
* Alert source. Defaults to "Splunk"
* (required)

action.thehive_create_alert.param.unique = <string>
* Field name that contains a unique identifier specific to the source event.
* (required)

action.thehive_create_alert.param.title = <string>
* Alert Title to use in theHive.
* (required)

action.thehive_create_alert.param.description = <string>
* The description of the alert to send to theHive.
* (required)

action.thehive_create_alert.param.tags = <string>
* The tags to put on the alert. Use a single, comma-separated string (ex. "badIP,trojan").
* (optional)

action.thehive_create_alert.param.severity = [0|1|2|3]
* The severity of the new alert. 1 = low, 2 = medium, 3 = high
* Default is "2" (medium)
* (optional)

action.thehive_create_alert.param.tlp = [-1|0|1|2|3]
* Traffic Light Protocol for this alert. 0 = White, 1 = Green, 2 = Amber, 3 = Red
* TLP affects releasability of information. Some analyzers will not be available on higher TLP settings.
* Defaults to "-1" (unset)
* (optional)
