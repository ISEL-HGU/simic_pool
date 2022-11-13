package poolprocess;

import org.eclipse.jgit.diff.DiffAlgorithm;
import org.eclipse.jgit.diff.DiffEntry;
import org.eclipse.jgit.diff.DiffFormatter;
import org.eclipse.jgit.diff.RawTextComparator;
import org.eclipse.jgit.lib.ObjectId;
import org.eclipse.jgit.lib.ObjectReader;
import org.eclipse.jgit.lib.Repository;
import org.eclipse.jgit.revwalk.RevCommit;
import org.apache.commons.collections4.IterableUtils;
import org.eclipse.jgit.revwalk.RevTree;
import org.eclipse.jgit.revwalk.RevWalk;
import org.eclipse.jgit.treewalk.TreeWalk;
import org.eclipse.jgit.util.io.DisabledOutputStream;

import javax.annotation.Nullable;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class Git {
    private final String workPath = "/data/CGYW/clones/";
    private DiffAlgorithm diffAlgorithm = DiffAlgorithm.getAlgorithm(DiffAlgorithm.SupportedAlgorithm.MYERS);
    private RawTextComparator diffComparator = RawTextComparator.WS_IGNORE_ALL;
    private org.eclipse.jgit.api.Git git;
    public String collect(String[] pairInfo) {
        String repoName = pairInfo[0];
        String cpc = pairInfo[1];
        String pc = pairInfo[2];
        String filePath = pairInfo[3];
        String line = pairInfo[4];

        Repository repository = getRepo(repoName);

        Iterable<RevCommit> walk;
        try {
            walk = git.log().all().call();
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
        List<RevCommit> commitList = IterableUtils.toList(walk);

        RevCommit pcCommit = null;
        for (RevCommit commit : commitList) {
            if (pcCommit != null) break;
            else if (commit.getId().getName().equals(pc)) pcCommit = commit;
        }

        RevCommit pcCommitParent = pcCommit.getParent(0);

        //pc.src - pc.dst
        String pcDiffString = collectDiff(pcCommitParent, pcCommit, repository, filePath);
        if ((pcDiffString.contains("rename from") && pcDiffString.contains("rename to")) ||
                pcDiffString.length() < 1) return null;

        String diffStrings = cropPCDiff(pcDiffString, line);

        return diffStrings;
    }

    public String collectDiff(RevCommit parent, RevCommit commit, Repository repository, String filePath) {
        List<DiffEntry> diffs = diff(parent, commit, repository);
        if (diffs == null) return null;
        String diffString = "";
        for (DiffEntry diff : diffs) {
            String oldPath = diff.getOldPath();
            String newPath = diff.getNewPath();
            if (oldPath.equals(filePath) || newPath.equals(filePath)) {
                ByteArrayOutputStream out = new ByteArrayOutputStream();
                try (DiffFormatter formatter = new DiffFormatter(out)) {
                    formatter.setRepository(repository);
                    formatter.setDiffAlgorithm(diffAlgorithm);
                    formatter.setDiffComparator(diffComparator);
                    formatter.setDetectRenames(true);
                    formatter.format(diff);
                    diffString = out.toString();
                } catch (IOException e) {
                    System.err.println("error: unable to get CPC-Diff");
                    e.printStackTrace();
                }
                break;
            }
        }
        return diffString;
    }

    public Repository getRepo(String RepoName) {
        try {
            File file = new File(workPath + "/" + RepoName + "/.git");

            if (file.exists()) git = org.eclipse.jgit.api.Git.open(file);
            else throw new IOException();
            return git.getRepository();
        } catch (IOException e) {
            e.printStackTrace();
        }
        return null;
    }

    public List<DiffEntry> diff(RevCommit parent, RevCommit commit, Repository repo) {
        DiffFormatter df = new DiffFormatter(DisabledOutputStream.INSTANCE);
        df.setRepository(repo);
        df.setDiffAlgorithm(diffAlgorithm);
        df.setDiffComparator(diffComparator);
        df.setDetectRenames(true);
        List<DiffEntry> diffs = null;
        try {
            diffs = df.scan(parent.getTree(), commit.getTree());
        } catch (IOException e) {
            e.printStackTrace();
        }
        return diffs;
    }

    public String cropPCDiff (String diffString, String line) {
        Pattern pattern = Pattern.compile("@@ -[0-9]+,[0-9]+ \\+[0-9]+,[0-9]+ @@\n", Pattern.CASE_INSENSITIVE);
        Matcher matcher = pattern.matcher(diffString);

        List<String> hunkInfo = new ArrayList<>();
        while (matcher.find()) {
            hunkInfo.add(matcher.group());
        }

        String[] hunks = diffString.split("@@ -[0-9]+,[0-9]+ \\+[0-9]+,[0-9]+ @@\n");

        int idx = 0;
        String targetHunk = "", diffFormat = "";
        boolean targetFound = false, changeRemoved = false;
        for (String hunk : hunks) {
            if (idx==0) {
                diffFormat = hunk;
                idx++;
                continue;
            }
            if (hunk.contains(line)) {
                //[Heuristic] #1
                if (hunk.contains("+")) {
                    targetHunk = hunk;
                    targetFound = true;
                }
                else {
                    changeRemoved = true;
                }
            }

            if (targetFound) break;
            else if (changeRemoved) break;
            idx++;
        }

        if (changeRemoved) {
            System.err.println("git: changes are all deleted");
            return null;
        }
        else if (targetHunk.isEmpty() || diffFormat.isEmpty()) {
            System.err.println("error: unable to get target hunk\n");
            return null;
        }

        return diffFormat + hunkInfo.get(idx-1) + targetHunk;
    }
}
