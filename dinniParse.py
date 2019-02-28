import json

diniString="Cufflinks,Cytoscape,exonerate,FreeBayes,Jellyfish,ABySS,angsd,Augustus,AUGUSTUS,BamTools,BBMap,BCFtools,BEAST,BEDOPS,BEDTools,BioConductor,Bismark,BLASR,blasr_libcpp,BLAST,BLAT,Bowtie,Bowtie2,Bpipe,BreakDancer,BUSCO,BWA,Canu,Classifier,Clustal-Omega,CNVnator,ctffind,cutadapt,DBG2OLC,DIAMOND,EMIRGE,ExaBayes,ExaML,FALCON,FastQC,Fastq-tools,fastStructure,FastTree,FASTX-Toolkit,GATK,GMAP-GSNAP,Gubbins,HISAT2,HMMER,HTSlib,IDBA,IGV,IMPUTE,Infernal,kallisto,Kraken2,MAFFT,MaSuRCA,MetaVelvet,Metaxa2,Mothur,MotionCorr,MrBayes,MultiQC,MUMmer,MUSCLE,ncbi-vdb,NGS,nseg,PBJelly,PhyML,picard,PLINK,pplacer,QIIME2,QUAST,RAxML,RECON,Relion,RepeatMasker,RepeatScout,RMBlast,RSEM,Salmon,Sambamba,samblaster,SAMtools,seqtk,snpEff,SOAPdenovo2,SortMeRNA,SourceTracker,SPAdes,sratoolkit,Stacks,STAR,Subread,swarm,TopHat,trf,TrimGalore,Trinity,VCFtools,Velvet,VSEARCH,Wise2"
diniArray=diniString.split(',')

with open('overwriteApps.json') as json_file: 
    data = json.load(json_file)
    for app in diniArray:
        data[app]={}
        data[app]["cats"]=['genomics']

print(json.dumps(data))



f = open("overwriteApps2.json", "a")
f.write(json.dumps(data))