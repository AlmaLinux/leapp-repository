from leapp.actors import Actor
from leapp.tags import FirstBootPhaseTag, IPUWorkflowTag
from leapp import reporting
from leapp.libraries.common.config import version

try:
    # py2
    import ConfigParser as configparser
    ParserClass = configparser.SafeConfigParser
except Exception:
    # py3
    import configparser
    ParserClass = configparser.ConfigParser


class EnableYumSpacewalkPlugin(Actor):
    """
    Enable yum spacewalk plugin if it's disabled
    Required for the CLN channel functionality to work properly
    """

    name = 'enable_yum_spacewalk_plugin'
    consumes = ()
    produces = ()
    tags = (FirstBootPhaseTag, IPUWorkflowTag)

    config = '/etc/yum/pluginconf.d/spacewalk.conf'

    def process(self):
        if (version.current_version()[0] != "cloudlinux"):
            return
        summary = 'yum spacewalk plugin must be enabled for the CLN channels to work properly. ' \
            'Please make sure it is enabled. Default config path is "%s"' % self.config
        title = None

        parser = ParserClass(allow_no_value=True)
        try:
            red = parser.read(self.config)
            if not red:
                title = 'yum spacewalk plugin config not found'
            if parser.get('main', 'enabled') != '1':
                parser.set('main', 'enabled', '1')
                with open(self.config, 'w') as f:
                    parser.write(f)
                self.log.info('yum spacewalk plugin enabled')
                return
        except Exception as e:
            title = 'yum spacewalk plugin config error: %s' % e

        if title:
            reporting.create_report([
                reporting.Title(title),
                reporting.Summary(summary),
                reporting.Severity(reporting.Severity.MEDIUM),
                reporting.Tags([reporting.Tags.SANITY])
            ])
