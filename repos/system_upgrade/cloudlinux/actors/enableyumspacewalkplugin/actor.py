from leapp.actors import Actor
from leapp.tags import FirstBootPhaseTag, IPUWorkflowTag
from leapp import reporting

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
    Enable yum spacewalk plugin if it disabled
    Needs to CLN channel work properly
    """

    name = 'enable_yum_spacewalk_plugin'
    consumes = ()
    produces = ()
    tags = (FirstBootPhaseTag, IPUWorkflowTag)

    config = '/etc/yum/pluginconf.d/spacewalk.conf'

    def process(self):
        summary = 'Yum spacewalk plugin must be enabled to CLN channel work properly. ' \
            'Please make sure it is enabled. Default config path is "%s"' % self.config
        title = None

        parser = ParserClass(allow_no_value=True)
        try:
            red = parser.read(self.config)
            if not red:
                title = 'Yum spacewalk plugin config not found'
            if parser.get('main', 'enabled') != '1':
                parser.set('main', 'enabled', '1')
                with open(self.config, 'w') as f:
                    parser.write(f)
                self.log.info('Yum spacewalk plugin enabled')
                return
        except Exception as e:
            title = 'Yum spacewalk plugin config error: %s' % e

        if title:
            reporting.create_report([
                reporting.Title(title),
                reporting.Summary(summary),
                reporting.Severity(reporting.Severity.MEDIUM),
                reporting.Tags([reporting.Tags.SANITY])
            ])
