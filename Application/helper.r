
library(readr)
lib <- read_csv("Data/All_Liberal_Sentiment.csv")
cons <- read_csv("Data/All_Conservative_Sentiment.csv")

### Clean Text
library(qdap)
library(tm)

lib_titles <- lib[['Title']]
con_titles <- cons[['Title']]

stopwords_regex = paste(stopwords('en'), collapse = '\\b|\\b')
stopwords_regex = paste0('\\b', stopwords_regex, '\\b')

lib_titles = stringr::str_replace_all(lib_titles, stopwords_regex, '')
lib_titles <- tolower(lib_titles)
lib_titles <- removePunctuation(lib_titles)
lib_titles <- removeNumbers(lib_titles)
lt <- freq_terms(lib_titles, top = 20, stopwords = Top200Words)

con_titles = stringr::str_replace_all(con_titles, stopwords_regex, '')
con_titles <- tolower(con_titles)
con_titles <- removePunctuation(con_titles)
con_titles <- removeNumbers(con_titles)
ct <- freq_terms(con_titles, top = 20, stopwords = Top200Words)

### Tree Map
library(treemap)
library(highcharter)

libs <- treemap(lt, 
                index = "WORD",
                vSize = "FREQ",
                type = "index",
                palette = "Blues",
                title = "R/Liberal Title",
                fontsize.title = 14)

Conserv <- treemap(ct,
                   index = "WORD",
                   vSize = "FREQ",
                   type = "index",
                   palette = "Reds")


### Sentiment Statistics
lm <- mean(lib[['Sentiment Mean_x']], na.rm = TRUE)
ls <- mean(lib[['Sentiment Std_x']], na.rm = TRUE)
lv <- mean(lib[['Sentiment Var_x']], na.rm = TRUE)

cm <- mean(cons[['Sentiment Mean_x']],na.rm = TRUE)
cs <- mean(cons[['Sentiment Std_x']], na.rm = TRUE)
cv<- mean(cons[['Sentiment Var_x']], na.rm = TRUE)

### Binning Data
library(ggplot2)

l <- vector("character",length(lib[['Sentiment Mean_x']]))
cons_s <- (vector("character",length(cons[['Sentiment Mean_x']])))
tags <- c("Very Strong Negative", "Strong Negative","Moderate Negative","Weak Negative","Neutral","Weak Positive","Moderate Positive","Strong Positive","Very Strong Positive")

lib_dataframe <- data.frame(l,lib[['Sentiment Mean_x']])
names(lib_dataframe) <- c("subreddit","sentiment")
lib_dataframe[lib_dataframe ==""]<- "Lib"


con_dataframe <- data.frame(cons_s,cons[['Sentiment Mean_x']])
names(con_dataframe)<- c("subreddit","sentiment")
con_dataframe[con_dataframe ==""]<- "Cons"
final_dataframe <- rbind(lib_dataframe,con_dataframe)


library(dplyr)

final_dataframe <- final_dataframe %>% 
  mutate("Type"=
           ifelse(between(sentiment,-1,-0.76),tags[1],
                  ifelse(between(sentiment,-0.75,-0.51),tags[2],
                         ifelse(between(sentiment,-0.5,-0.251),tags[3],
                                ifelse(between(sentiment,-0.25,-0.06),tags[4],
                                       ifelse(between(sentiment,-0.05,0.05),tags[5],
                                              ifelse(between(sentiment,0.06,0.25), tags[6],
                                                     ifelse(between(sentiment,0.251, 0.5), tags[7],
                                                            ifelse(between(sentiment,0.51,0.75),tags[8],tags[9])))))))))

lib_type <- final_dataframe %>% filter(subreddit=="Lib")
cons_type <- final_dataframe %>% filter(subreddit=="Cons")


tc <- read_csv("Data/trump_cons.csv")
bc <- read_csv("Data/biden_cons.csv")
kc <- read_csv("Data/kamala_cons.csv")
pc <- read_csv("Data/pence_cons.csv")
tl <- read_csv("Data/trump_lib.csv")
bl <- read_csv("Data/biden_lib.csv")
kl <- read_csv("Data/kamala_lib.csv")
pl <- read_csv("Data/pence_lib.csv")

tcc <- mean(tc[['Sentiment']])
bcc <- mean(bc[['Sentiment']])
kcc <- mean(kc[['Sentiment']])
pcc <- mean(pc[['Sentiment']])

tlc <- mean(tl[['Sentiment']])
blc <- mean(bl[['Sentiment']])
klc <- mean(kl[['Sentiment']])
plc <- mean(pl[['Sentiment']])
