import sqlite3 as lite
import sys
import os
import threading
import gbk_parser
import ucsc_parser
records = gbk_parser.records

def write_aliases():
    print("writing aliases.txt")
    with open("aliases.txt","w") as aliases_file:
        aliases = set()
        for record in records:
            features = [feature for feature in record.features if feature.type == "CDS"]
            for feature in features:
                gene_aliases =""
                gene_name =""
                if "gene" in feature.qualifiers:
                    gene_name = feature.qualifiers["gene"][0]
                if "gene_synonym" in feature.qualifiers:
                    gene_aliases = feature.qualifiers["gene_synonym"][0]
                if gene_name:
                    aliases.add(gene_name + ";" + gene_aliases)
        for aliase in aliases:
            aliases_file.write(aliase +"\n")



def create_aliases_db():
    # create database of aliases
    with open('db/transcript_aliases.txt','r') as f:
        aliases_lines = f.readlines()
    values_keys = [tuple(line.replace('\n','').split('\\t')) for line in aliases_lines]
    zipped = [(key,value) for value,key in values_keys]
    aliases_dict = dict(zipped)
    with lite.connect('db/aliases.db') as con:
        print ("Creating aliases database...")
        cur = con.cursor()
        cur.execute("CREATE TABLE genes(Id INT, symbol TEXT, aliases TEXT, transcript_id TEXT)")
        index=0
        with open("aliases.txt","r") as aliases_file:
            for gene_aliases in aliases_file.readlines():
                for alias in gene_aliases.split(";"):
                    if alias != "" and alias !="\n":
                        for name in gene_aliases.split(";"):
                            transcript_id = aliases_dict.get(name,'')
                            if transcript_id != '':
                                break
                        cur.execute("INSERT INTO genes VALUES(?,?,?,?)",(index,alias,gene_aliases,transcript_id))
                        index +=1
        print ("Aliases database created")

def create_transcript_data_db():
    print ("Creating transcript data db...")
    with lite.connect('db/transcript_data.db') as con:
        names = ucsc_parser.parse_knownGene(ucsc_parser.knownGene_path)
        cur = con.cursor()
        cur.execute("CREATE TABLE transcripts(name TEXT,\
                    chrom TEXT,\
                    strand TEXT,\
                    tx_start TEXT,\
                    tx_end TEXT,\
                    cds_start TEXT,\
                    cds_end TEXT,\
                    exon_count TEXT,\
                    exon_starts TEXT,\
                    exon_ends TEXT,\
                    protein_id TEXT,\
                    align_id TEXT)")

        for name in names:
            values = tuple(names[name].values())
            cur.execute("INSERT INTO transcripts VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",values)

def create_comb_db():
    with lite.connect('db/comb.db') as con:
        print("Creating database...")
        cur = con.cursor()
        cur.execute("CREATE TABLE genes(Id INT, symbol TEXT, db_xref TEXT, coded_by TEXT, chromosome TEXT,strain TEXT, cds TEXT, sites TEXT, regions TEXT)")
        for index,record in enumerate(records):
            sites=[]
            regions=[]
            cds = []
            location = ""
            name =""
            db_xref=""
            coded_by =""
            chromosome =""
            strain = ""
            for feature in record.features:
                if feature.type == 'source':
                    if 'strain' in feature.qualifiers:
                        strain = feature.qualifiers['strain'][0]
                    if 'chromosome' in feature.qualifiers:
                        chromosome = feature.qualifiers['chromosome'][0]
                if feature.type == 'CDS':
                    cds.append(str(feature))
                    name=feature.qualifiers['gene'][0]
                    coded_by = feature.qualifiers['coded_by'][0]
                    db_xref = feature.qualifiers['db_xref'][0]
                    location = str(feature.location)
                if feature.type == 'Site':
                    sites.append(feature.qualifiers['site_type'][0]+str(feature.location))
                if feature.type == 'Region':
                    regions.append(feature.qualifiers['region_name'][0]+str(feature.location))
            sites_comb = ','.join(sites)
            region_comb = ','.join(regions)
            cds_comb = ','.join(cds)
            if sites_comb == '' and sites_comb == '' and region_comb == '':
                continue
            cur.execute("INSERT INTO genes VALUES(?, ?, ?, ?, ?, ?,  ?, ?,?)",(index,name,db_xref,coded_by,chromosome,strain,cds_comb,sites_comb,region_comb))
            index+=1


if __name__ == "__main__":
    t_1 = threading.Thread(target=create_comb_db)
    t_1.start()
    write_aliases()
    create_aliases_db()
    create_transcript_data_db()