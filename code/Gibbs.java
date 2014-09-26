/******************************************************************************
Collapsed Gibbs sampling for latent Dirchlet allocation on images.

Infers topic allocations per word, per doc; from which topic proportions and 
word-topic distributions can be derived. Outputs CDWT, CDT, and CWT files every 
(#iterations/3)th iteration (file format as per CDW).

    usage: java Gibbs inputfile #topics #iterations

NOTE: can be used for other types of data (eg a document 
corpus), so long as the CDW matrix is input in the required format.

TODO: optimise alpha and beta vectors (instead of using lame heuristic values),
implement "perplexity", let either CWD or CDWT be read in


By Anna Friedlander
email anna.fr@gmail.com

Slightly adapted for text by Marcus Frean.

******************************************************************************/
import java.util.*;
import java.io.*;

public class Gibbs{
    //number of topics, words in vocab, documents
    private int D;
    private int V;
    private int T;
    //alpha and beta hyperparameters
    private double alpha = 0.1;
    private double beta = 0.01;
    //matrices
    private int    [][] CDW;
    private int    [][][] CDWT;
    private double [][]   CWT;
    private double [][]   CDT;
    private double []     CT;
    private double []     probs;
    //arrays for word and doc names
    private String [] wordnames;
    private String [] docnames;
    private String directory;
    
    /*fill matrices, run Gibbs, and print final CWT and CDT*/
    public Gibbs(String fname, int numtopics, int iters){
	long start = System.currentTimeMillis();
	
	//get number of topics
	T=numtopics;
	
	//fill matrices
	matrices(fname);
	directory = fname;

	//Gibbs
	System.out.println("HERE WE GO");
	gibbs_sampling(iters, iters);
	
	long end = System.currentTimeMillis();
	print_times(start, end, "TOTAL TIME:");
    }
    
    
    /* make CDWT, CWT, CDT matrices and initialise D & V parameters */
    public void matrices(String infile){
	
	System.out.println("reading infile and making matrices");
	Random rdm = new Random();
	
	//read CDW file in
	try{
	    File fp = new File(infile);
	    Scanner scan = new Scanner(fp).useDelimiter(",");
	    // Figure out V, the size of the vocabulary.
	    String[] elts = scan.nextLine().split(",");
	    System.out.printf("The first thing on the line was  %s \n",elts[0]);
	    V=elts.length-1;
	    wordnames = new String[V];
	    for (int i=0;i<V;i++) wordnames[i] = elts[i+1].trim();

	    // Read the lines in. But we don't know how many there
	    // are.  Can either read them in twice, or read into an
	    // arraylist and convert to an array at end. I will try
	    // the latter.
	    D=0;
	    List <int[]> list = new ArrayList<int[]>();
	    List <String> names = new ArrayList<String>();
	    while (scan.hasNext()) {
		elts = scan.nextLine().split(",");
		int[] tmp = new int[V];
		// the first column is the name of the document, and the rest are counts.
		names.add(elts[0].trim());
		for (int i=0;i<V;i++)  tmp[i] = Integer.parseInt(elts[i+1].trim());
		list.add(tmp);
		D++;
	    }
	    scan.close();
	    CDW = list.toArray(new int[list.size()][]);
	    
	    docnames  = new String[D];
	    for (int d=0;d<D;d++) docnames[d] = names.get(d);

	    // Just a quick check...
	    if (D< 10) 
		for (int d=0;d<D;d++) {
		    System.out.printf("%12s:  ",docnames[d]);
		    for (int w=0;w<V;w++) 
			System.out.printf("%3d ",CDW[d][w]);
		    System.out.printf("\n");
		}
	    System.out.printf("%d docs and  a vocabulary of  %d words \n", D,V);
	    for(int d=0;d<5;d++)
		System.out.printf("Document %d is %s \n",d,docnames[d]);
	    
	    CDWT = new int   [D][V][T];
	    //fill in CDWT
	    for(int d=0;d<D;d++)
		for(int v=0;v<V;v++)
		    //initialise topics randomly
		    for(int i=0;i<CDW[d][v];i++)	CDWT[d][v][rdm.nextInt(T)] += 1;
        }
        catch(IOException e){
            System.out.println("File reading failed: "+e);
            System.exit(1);
	}
	
	//fill in the supporting matrices
	CWT  = new double[V][T];
	CDT  = new double[D][T];
	CT   = new double[T];
	probs= new double[T];

	for(int v=0;v<V;v++)
	    for(int t=0;t<T;t++) {
		int sum =0;
		for(int d=0;d<D;d++) sum += CDWT[d][v][t];
		CWT [v][t]  = sum + beta;
	    }

	for(int t=0;t<T;t++) {
	    CT [t]  = 0.0;
	    for(int v=0;v<V;v++) CT[t] += CWT[v][t];
	}

	for(int d=0;d<D;d++) 
	    for(int t=0;t<T;t++) {
		int sum = 0;
		for(int v=0;v<V;v++) sum += CDWT[d][v][t];
		CDT [d][t] = sum + alpha;
	    }
	System.out.println("reading infile and making matrices done");
    }
    

    /* Gibbs sampling */
    public void gibbs_sampling(int iters, int n){
	
	System.out.println("starting Gibbs");
	int iter = iters;
	int dvt,  zi;
	double num, sum;
	
	for(int i=1;i<iter+1;i++){
	    if((i%10) == 0) System.out.println("iter "+i);
	    for(int d=0;d<D;d++){
		for(int v=0;v<V;v++){
		    for(int t=0;t<T;t++){
			dvt = CDWT[d][v][t];
			for(int g=0;g<dvt;g++){
			    //decrement entry in matrices corresponding to topic
			    CDWT[d][v][t] -= 1;
			    CWT [v][t]   -= 1;
			    CDT [d][t]   -= 1;
			    CT  [t]     -= 1;
			    //calculate(zi = j) the probability of the current topic 
			    //assignment given the current distribution
			    sum = 0;
			    for(int j=0;j<T;j++){
				num = CWT[v][j]/CT[j] * CDT[d][j];
				probs[j] = num;
				sum += num;
			    }
			    //normalise
			    for(int j=0;j<T;j++) probs[j] /= sum;
			    //convert to cummulative distribution function
			    for(int j=1;j<T;j++) probs[j] += probs[j-1];
			    //assign token zi a topic based on new probabilities (drawn 
			    //from a categorical distribution with parameters in probs)
			    Random rand = new Random();
			    double val = rand.nextDouble();
			    zi = binsearch(probs,val);
			    //increment entries in matrices corresponding to new topic
			    CDWT[d][v][zi] += 1;
			    CWT [v][zi]   += 1;
			    CDT [d][zi]   += 1;
			    CT  [zi]     += 1;
			}   
		    }
		}
	    }
	    if((i%n)  == 0) print(("iter"+i),CWT,CDT);
	}
	System.out.println("Gibbs done");
	
	/*
	  System.out.println("printing final CWT and CDT matrices");
	  print("final",CWT,CDT);
	  System.out.println("done printing matrices");
	*/
	
    }
    
    
    /*print CWT and CDT matrices
      TODO: address redundancy */
    public void print(String label, double[][]cwt, double[][]cdt){
	String OUT;
	PrintStream out;
	System.out.println("Printing the matrices...");
	try{
	    //print CDWT
	    /*
	    String OUT = directory.replace("DW","DWT");
	    PrintStream out = new PrintStream(new File(OUT));
	    out.printf("#%s %s %s %s\n",D,V,T,label);
	    for(int d=0;d<D;d++){
		out.printf("%s",docnames[d]);
		for(int t=0;t<T;t++) out.printf(",  %s ",t);
		out.printf("\n");
		for(int v=0;v<V;v++){
		    out.printf("%s",wordnames[v]);
		    for(int t=0;t<T;t++) out.printf(",  %.3f ",cwt[v][t]);
		    out.printf("\n");
		}
	    }
	    out.close();
	    System.out.printf("Wrote %s\n",OUT);
	    */
	    
	    //print CWT
	    OUT = directory.replace("DW","WT");
	    out = new PrintStream(new File(OUT));
	    out.printf("%s",label);
	    for(int t=0;t<T;t++) out.printf(",  topic%s",t);
	    out.printf("\n");
	    for(int v=0;v<V;v++){
		out.printf("%s",wordnames[v]);
		for(int t=0;t<T;t++)
		    out.printf(",  %.3f",cwt[v][t]);
		out.printf("\n");
	    }
	    out.close();
	    System.out.printf("Wrote %s\n",OUT);
	    
	    //print CDT
	    OUT = directory.replace("DW","DT");
	    //OUT = (label + "_CDT.csv");
	    out = new PrintStream(new File(OUT));
	    out.printf("%s",label);
	    for(int t=0;t<T;t++) out.printf(",  topic%s",t);
	    out.printf("\n");
	    for(int d=0;d<D;d++){
		out.printf("%s",docnames[d]);
		for(int t=0;t<T;t++)
		    out.printf(",  %.3f",cdt[d][t]);
		out.printf("\n");
	    }
	    out.close();
	    System.out.printf("Wrote %s\n",OUT);
	}catch(IOException e){System.out.println("File writing failed: "+e);}
    }
    
    
    /*binary search*/
    public int binsearch(double[]probs, double val){
	int lo = 0;
	int hi = probs.length - 1;
	int mid;
	while(lo <= hi){
	    mid = (lo+hi)/2;
	    if(probs[mid] > val)      hi = mid-1;
	    else if(probs[mid] < val) lo = mid+1;
	    else                      return mid;
	}
	return lo;
    }
    
    
    
    /*helper method to time program*/
    public void print_times(long start, long stop, String message){
	long time = stop-start;
	System.out.println(message);
	System.out.println("mins: "+time/(60*1000F));
	System.out.println("secs: "+time/1000F);
    }
    
    
    /*input format: java Gibbs inputfile outstem iterations*/
    public static void main(String args[]){
	String input,message="usage: java Gibbs CWD-inputfile #topics #iterations";
	int topics=0,iters=0;
	
	if(args.length != 3){System.out.println(message);System.exit(1);}
	
	try{ 
	    topics = Integer.parseInt(args[1]);
	}catch(NumberFormatException e){System.out.println(message);System.exit(1);}
	
	try{ 
	    iters = Integer.parseInt(args[2]);
	}catch(NumberFormatException e){System.out.println(message);System.exit(1);}
	
	input = args[0];
	new Gibbs(input,topics,iters);
    }
    
}


