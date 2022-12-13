
suppressPackageStartupMessages({
  library(DT)
  library(data.table)
  library(dplyr)
  library(RColorBrewer)
  library(gganatogram) 
  library(ontologyIndex)
  library(ontologySimilarity)
})



##### 
# Read phenotype data
pheno <- fread("/s/project/mitoMultiOmics/metabolomics/metabolomics_annotation/mitoNET_annotation/mitoNET_HPO_annotation.txt")
pheno <- pheno[pseudonym %in% sa$pseudonym ]
pheno <- pheno[, c("pseudonym" , "HPO_ID")] 

# load HPO ontology
hpo <- get_ontology("http://purl.obolibrary.org/obo/hp.obo", extract_tags="everything")

pheno <- pheno[ HPO_ID %in% unique(hpo$id)]
pheno <- pheno[!duplicated(pheno)]

# Extract HPO terms level 3 = organ systems
hpo_ID_to_hpo_term <- pheno[, c("HPO_ID")] 
hpo_ID_to_hpo_term <- hpo_ID_to_hpo_term[!duplicated(hpo_ID_to_hpo_term)]
hpo_ID_to_hpo_term$umbrella_HPO_term <- lapply(hpo_ID_to_hpo_term$HPO_ID, function(hpo_id) {
  get_term_property(ontology=hpo, property="ancestors", term=hpo_id, as_names=TRUE)[3]
})
hpo_ID_to_hpo_term <- hpo_ID_to_hpo_term %>% 
  mutate_at('umbrella_HPO_term', paste)
#str(hpo_ID_to_hpo_term)
pheno <- merge(pheno, hpo_ID_to_hpo_term, by = "HPO_ID")




# only keep a system once per patient
gene_man <- pheno[, c("pseudonym",  "umbrella_HPO_term")]
gene_man <- gene_man[ umbrella_HPO_term != "NA"]
gene_man <- gene_man[!duplicated(gene_man)]
gene_man[, sys_freq := .N, by = c("umbrella_HPO_term")]
gene_man[ , prop_system :=  sys_freq / uniqueN(gene_man$pseudonym)]
gene_man$pseudonym <- NULL
gene_man <- gene_man[!duplicated(gene_man)]



# Colour code by proportion
col_pur <- brewer.pal(n = 11, name = "PuOr")
gene_man[prop_system > 0 & (prop_system <= 0.10), colour := "grey90"]
gene_man[prop_system > 0.10 & (prop_system <= 0.2), colour := col_pur[7]]
gene_man[prop_system > 0.2 & (prop_system <= 0.3), colour := col_pur[8]]
gene_man[prop_system > 0.3 & (prop_system <= 0.5), colour := col_pur[9]]
gene_man[prop_system > 0.5, colour := col_pur[11]]
setnames(gene_man,"umbrella_HPO_term", "type")

###################################
# create anatomy maps
#unique(gene_man$umbrella_HPO_term)
male_organs <- as.data.table(hgMale_key) 
male_organs$value <- NULL
male_organs$colour <- NULL # colour encoded in gene_man

male_organs[organ %in%  c("caecum", "colon", "duodenum", "esophagus", "gastroesophageal_junction", "ileum",
                          "liver", "rectum", "small_intestine", "stomach"), type:= "Abnormality of the digestive system" ]
male_organs[organ %in%  c("urinary_bladder", "kidney"), type:= "Abnormality of the genitourinary system" ]
male_organs[organ %in%  c("amygdala", "brain", "cerebral_cortex", "cerebellum", "cerebellar_hemisphere", "hippocampus", "frontal_cortex", "nerve",
                          "prefrontal_cortex", "temporal_lobe"), type:= "Abnormality of the nervous system" ]
male_organs[organ %in%  c("skeletal_muscle"), type:= "Abnormality of the musculoskeletal system"]
male_organs[organ %in%  c("heart"), type:= "Abnormality of the cardiovascular system"]
male_organs[organ %in%  c("lung"), type:= "Abnormality of the respiratory system"  ]
male_organs[organ ==  "lymph_node"   , type:= "Abnormality of the immune system"] 
male_organs[organ %in%  c("thyroid_gland", "pituitary_gland", "adrenal_gland")   , type:= "Abnormality of the endocrine system"]  

male_organs[organ %in%  c("bone_marrow")   , type:= "Abnormality of blood and blood forming tissues"] 


# missing

# "Abnormality of head or neck"
# "Growth abnormality"  
# "Abnormality of limbs" 
# "Abnormality of metabolism/homeostasis"
# "Onset"  

male_organs <- male_organs[organ !=  "nerve"] # too many 
male_organs <- male_organs[organ !=  "spinal_cord"] # too many 
male_organs <- male_organs[!duplicated(male_organs)]



# keep table of eye and ear
ear_eye <- gene_man[type %in% c("Abnormality of the eye", "Abnormality of the ear")]

# Merge organ map with DATA
merge_HPO <- merge(gene_man, male_organs, by= "type", allow.cartesian=TRUE ,all.y = T)    # ,all.y = T ?


# New column, ordered type. for Order?
merge_HPO[, gene_freq:= factor(type, levels = rev(c("Abnormality of the cardiovascular system", 
                                                    "Abnormality of the respiratory system", 
                                                    "Abnormality of the genitourinary system",
                                                    "Abnormality of the digestive system", 
                                                    "Abnormality of the endocrine system", 
                                                    "Abnormality of the immune system",
                                                    "Abnormality of the musculoskeletal system", 
                                                    "Abnormality of the nervous system")))]

merge_HPO <- setorder(merge_HPO, type)

merge_HPO[, gene_freq:= factor(organ, levels = unique(merge_HPO$organ))]
merge_HPO <- setorder(merge_HPO, -organ)



male <- gganatogram(data=merge_HPO, fillOutline='white', organism='human', sex= "male", fill="colour") + theme_void()

# add eyes and ears

eye_col <- ear_eye[type == "Abnormality of the eye"]$colour
if(length(eye_col) == 0){
  eye_col <- "white"
}

ear_col <- ear_eye[type == "Abnormality of the ear"]$colour
if(length(ear_col) == 0){
  ear_col <- "white"
}

male <- male + 
  #eyes
  geom_point(aes(x = 49.5, y = -14), size = 2, colour = "grey35", fill=eye_col, shape=21, stroke = .15) + geom_point(aes(x = 56.5, y = -14), size = 2, colour = "grey35", fill=eye_col, shape=21, stroke = .15) +
  #ears
  geom_point(aes(x = 45, y = -16), size = 2, colour = "grey35", fill=ear_col, shape=23, stroke = .15) + geom_point(aes(x = 61, y = -16), size = 2, colour = "grey35", fill=ear_col, shape=23, stroke = .15)

# add scale
scale_dt <- data.table(x = c(0,0,0,0), y = c(-150,-160,-170,-180), colour = c(col_pur[7], col_pur[8], col_pur[9], col_pur[11]))

male <- male + 
  geom_point(aes(x = 0, y = -140), size = 5, colour = "grey90") + annotate(geom="text", x=10, y=-140, label="≤10%", size = 3) +
  geom_point(aes(x = 0, y = -150), size = 5, colour = col_pur[7]) + annotate(geom="text", x=17, y=-150, label=">10% and ≤20%", size = 3) +
  geom_point(aes(x = 0, y = -160), size = 5, colour = col_pur[8]) + annotate(geom="text", x=17, y=-160, label=">20% and ≤30%", size = 3) +
  geom_point(aes(x = 0, y = -170), size = 5, colour = col_pur[9]) + annotate(geom="text", x=17, y=-170, label=">30% and ≤40%", size = 3) +
  geom_point(aes(x = 0, y = -180), size = 5, colour = col_pur[11]) + annotate(geom="text", x=10, y=-180, label=">50%", size = 3)

#+ fig.width=8, fig.height=10
male + ggtitle("Phenotype frequency")+ theme(plot.title = element_text(face="bold", hjust = 0.5))





