package poolprocess;

import org.apache.commons.cli.*;

public class CLI {
    private static String[] diffInfo;

    public CLI (String[] args) {
        Options options = createOptions();
        parseOptions(options, args);
    }

    public String[] getDiffInfo() { return diffInfo; }

    private static boolean parseOptions(Options options, String[] args) {
        CommandLineParser parser = new DefaultParser();
        try {
            CommandLine cmd = parser.parse(options, args);

            String Project = cmd.getOptionValue("proj");
            String CPC = cmd.getOptionValue("cpc");
            String PC = cmd.getOptionValue("pc");
            String filePath = cmd.getOptionValue("file");
            String line = cmd.getOptionValue("line").replace("\"\"", "");
//            if (line.endsWith("]]")) line = line.substring(0, line.length()-3);
            diffInfo = new String[]{Project, CPC, PC, filePath, line};

        } catch (Exception e) {
            e.printStackTrace();
            return true;
        }
        return false;
    }

    private static Options createOptions() {
        Options options = new Options();

        options.addOption(Option.builder("proj")
                .required()
                .desc("Name of the pc/cpc commit project")
                .hasArg()
                .argName("https://github.com/[author/projectName]")
                .build());

        options.addOption(Option.builder("cpc")
                .required()
                .desc("")
                .hasArg()
                .argName("Change-Prone-Commit hashcode")
                .build());

        options.addOption(Option.builder("pc")
                .required()
                .desc("")
                .hasArg()
                .argName("Post-Commit hashcode")
                .build());

        options.addOption(Option.builder("file")
                .required()
                .desc("Path of the target file")
                .hasArg()
                .argName("file path")
                .build());

        options.addOption(Option.builder("line")
                .required()
                .desc("")
                .hasArg()
                .argName("line")
                .build());

        return options;
    }
}
