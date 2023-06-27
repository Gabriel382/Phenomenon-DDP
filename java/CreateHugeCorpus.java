package test;

import java.net.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;

import gate.*;
import gate.persist.SerialDataStore;
import gate.util.Err;
import gate.util.Out;

import gate.creole.ResourceInstantiationException;
import gate.util.GateException;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.PrintWriter;
import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.Writer;

public class CreateHugeCorpus {
	//the directory must EXIST and be EMPTY
	  //private static final String dsDir = "/var/tmp/gate001";
	  private static final String DS_DIR = "Path_to_directory_to_save_it";
	  private static final String DS_FOLDER = "Path_to_txt_with_list_of_folders_with_the_documents";
	  private static final String DS_FILE = "Path_to_txt_file_that_will_save_all_checkpoints_of_files_already_processed";
	  private static final String DS_FILEREAD = "Path_to_txt_with_list_of_folders_for_the_files_to_read_in_DS_Folder";
	  private static File dir_dsi;
	  private static String CorpusID = "PreDiViD___1678776628822___223"; 
	  
	  
	    public static void main(String args[]) {
	    	
	    	// init gate
	    	try {
	    	      Gate.init();
		    }
	    	    catch (GateException gex) {
	    	      Err.prln("cannot initialise GATE...");
	    	      gex.printStackTrace();
	    	      return;
		    }
  	      
	    	try {
	    		// =================================== CREATE DATASTORE ===========================================================
		    	//create&open a new Serial Data Store
	  	      //pass the datastore class and path as parameteres
	    		//SerialDataStore sds  = (SerialDataStore)Factory.createDataStore("gate.persist.SerialDataStore",DS_DIR);
	    		SerialDataStore sds = new SerialDataStore(DS_DIR);
	    		sds.open();
	  	      Out.prln("serial datastore created...");

	  	      // load corpus from datastore using its persistent ID
    	      //Object corpusID  = persistCorp.getLRPersistenceId();
    	      //persistCorp = null;
	  	      	
    	      FeatureMap corpFeatures = Factory.newFeatureMap();
    	      corpFeatures.put(DataStore.LR_ID_FEATURE_NAME, CorpusID);
    	      corpFeatures.put(DataStore.DATASTORE_FEATURE_NAME, sds);
    	      //tell the factory to load the Serial Corpus with the specified ID from the specified  datastore
    	      Corpus persistCorp = (Corpus)Factory.createResource("gate.corpora.SerialCorpusImpl", corpFeatures);
    	      Out.prln("corpus loaded from datastore...");
	  	      
	  	      //save corpus in datastore
	  	      //    SecurityInfo is ingored for SerialDataStore - just pass null
	  	      //    a new persisent corpus is returned
    	      /*Corpus corp = Factory.newCorpus("PreDiViD");
	  	      Corpus persistCorp = null;
	  	      persistCorp = (Corpus)sds.adopt(corp);
	  	      sds.sync(persistCorp);
	  	      Out.prln("corpus saved in datastore...");
	  	      //change corpus and sync it with the datastore
	  	      persistCorp.setName("PreDiViD");
	  	      persistCorp.sync();
	  	      Out.prln("corpus ID: " + persistCorp.getLRPersistenceId());*/
	  	      
	  	 // =================================== CREATE DATASTORE ===========================================================
	  	      
		    	File dir = new File("/home/alencga1/Documents/PreDiViD/git/predivid/code/IE/data/Aylien_covid_news_data/dates_text");
		    	for (File file : dir.listFiles()) {
		    		
		            if (file.isDirectory() && !CheckPath(file.getAbsolutePath(), DS_FOLDER) && CheckPath(file.getAbsolutePath(), DS_FILEREAD)) {
		                System.out.println("Directory: " + file.getAbsolutePath());
		                for(File textfile : file.listFiles()) {
		                	Document doc1 = Factory.newDocument(textfile.toURI().toURL());
		                	if(doc1 == null || InFileList(textfile.getAbsolutePath(), DS_FILE))
		                		continue;
		                	doc1.setName(textfile.getName());
		                	persistCorp.add(doc1);
		                	persistCorp.sync();
		                	AppendLine(textfile.getAbsolutePath(), DS_FILE);
		                	persistCorp.unloadDocument(doc1);
		                }
		                clearFile(DS_FILE);
		                AppendLine(file.getAbsolutePath(), DS_FOLDER);
		                System.out.println("Done");
		            } else {
		                System.out.println("Directory not registred: " + file.getAbsolutePath());
		            }
		        }
			  	 // =================================== CLOSE DATASTORE ===========================================================
		    	//close data store
	    	      sds.close();
		    	
	    	} catch(Exception ex) {
	    		ex.printStackTrace();
	    	}
	    }
	    
	    private static boolean InFileList(String filePath, String dsFile) {
			if(dir_dsi == null)
				dir_dsi = new File(dsFile);
			try {
		          long line_count = Files.lines(dir_dsi.toPath()).count();
		          if(line_count > 0) {
		        	  BufferedReader bufferedReader = Files.newBufferedReader(dir_dsi.toPath(), StandardCharsets.UTF_8);
		        	  String line;
		                while ((line = bufferedReader.readLine()) != null) {
		                	if(line.equals(filePath))
		                		return true;
		                }
		          }
		      } catch (IOException e) {
		          e.printStackTrace();
		      }
			return false;
		}

		public static boolean CheckPath(String absoluteFilePath, String dsFolder) {
	    	File dir = new File(dsFolder);
	    	try (BufferedReader bufferedReader = Files.newBufferedReader(dir.toPath(), StandardCharsets.UTF_8)) {
                String line;
                while ((line = bufferedReader.readLine()) != null) {
                	if(line.equals(absoluteFilePath))
                		return true;
                }
            } catch (IOException ex) {
                System.out.format("I/O error: %s%n", ex);
            }
			return false;
		}

		public static void AppendLine(String text, String my_file_name) {
	    	try {
		    	Writer output;
		    	output = new BufferedWriter(new FileWriter(my_file_name, true));
		    	output.append(text + "\n");
		    	output.close();
	    	} catch(Exception ex) {
	    		ex.printStackTrace();
	    	}
	    }
	    
	    public static void clearFile(String path)

	    { 

	        try{

	        FileWriter fw = new FileWriter(path, false);
	        PrintWriter pw = new PrintWriter(fw, false);
	        pw.flush();
	        pw.close();
	        fw.close();
	        }catch(Exception exception){

	            System.out.println("Exception have been caught");

	        }

	    }
	    
	    public static String FileToString(File textfile) {
	    	String result = "";
	    	if(textfile.isFile()) {
        		try (BufferedReader bufferedReader = Files.newBufferedReader(textfile.toPath(), StandardCharsets.UTF_8)) {
                    String line;
                    while ((line = bufferedReader.readLine()) != null) {
                    	result = result + "\n" + line;
                    }
                } catch (IOException ex) {
                    System.out.format("I/O error: %s%n", ex);
                }
        	}
	    	return result;
	    }
	    
}
