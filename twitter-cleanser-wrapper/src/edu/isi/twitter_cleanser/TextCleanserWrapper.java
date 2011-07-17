package edu.isi.twitter_cleanser;

import java.io.*;

public class TextCleanserWrapper {
	private Process p;
	private BufferedReader stdInput;
	private BufferedWriter stdOutput;
	private BufferedReader stdErr;
	
	public TextCleanserWrapper() {
		try {
			ProcessBuilder builder = new ProcessBuilder();
			if(System.getenv().get("TEXT_CLEANSER_HOME") == "") {
				System.err.println("Environment variable TEXT_CLEANSER_HOME must be set");
				System.exit(-1);
			}
			else {
				System.out.println("Running " + System.getenv("TEXT_CLEANSER_HOME"));
			}
			// manual override for now
//			String clnsHome="/media/Data/work/Development/EclipseWorkspace/TextCleanser/penguin-src"; //System.getenv("TEXT_CLEANSER_HOME");
			String clnsHome=System.getenv().get("TEXT_CLEANSER_HOME");
			builder.directory(new File(clnsHome+"/"));
			builder.command(clnsHome + "/cli_cleanser.py");
			this.p = builder.start();
			this.stdInput  = new BufferedReader(new InputStreamReader(p.getInputStream()));
			this.stdOutput = new BufferedWriter(new OutputStreamWriter(p.getOutputStream()));
			this.stdErr    = new BufferedReader(new InputStreamReader(p.getErrorStream()));
			
			// wait for cleanser to display READY status
//			System.out.println("1");
//			String thisLine = this.stdInput.readLine();
//			System.out.println("2");
//			System.out.println(thisLine);
//			System.out.flush();
//			
			/*while ((thisLine = stdInput.readLine()) != null) {
				System.out.println(thisLine);
				if (thisLine.contains("READY")) {
					break;					
				}				
			}*/
			
		} catch (IOException e) {
			e.printStackTrace();
			System.exit(-1);
		}
	}
	
	public String cleanseTweet(String text) {
		try {
			this.stdOutput.write(text + "\n");
			this.stdOutput.flush();
			String result = this.stdInput.readLine();
			System.out.println("Output: " + result);
			while(this.stdErr.ready()) {
				System.out.println(this.stdErr.readLine());
			}
//			System.out.println("Result: " + result);
			return result;
		} catch (IOException e) {
			e.printStackTrace();
			System.exit(-1);
		}
		return "";
	}
}
