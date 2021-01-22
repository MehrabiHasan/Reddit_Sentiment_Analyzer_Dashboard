library(shiny)
library(highcharter)
library(dplyr)
library(Rcpp)
library(DT)
library(shinydashboard)
library(shinythemes)
library(shinyBS)
library(readr)
library(qdap)
library(tm)
library(treemap)
library(d3Tree)
library(ggplot2)
library(htmltools)
library(shinyjs)
library(magrittr)

library(rsconnect)

source("helper.r")

#High Charter Theme For Plots
thm <- hc_theme(colors = c('red','green','blue'),
                chart = list(backgroundColor = "#2b3e50"),
                title = list(style = list(color ='white')),
                subtitle = list(style = list(color ='white',
                                             fontFamily = "Shadows Into Light")),
                legend = list(itemStyle = list(color ='white')
                              ,itemHoverStyle = list(color ='gray')))

#Reading in Data


ui <- fluidPage(theme = shinytheme("superhero"),
    
    fluidRow(class= "Row0", style = "background-color: #4d3a7d; padding: 10px;",
      actionButton("btn","Learn More", class = "pull-right"),
      titlePanel("Reddit Political Dashboard"),
      titlePanel(h3("Text Analysis between R/Liberal and R/Conservative")),
      bsTooltip("btn",
                'This is a Dashboard serves to show the difference in political opinions in social media. For demonstration purposes, we decided to use two different communities on Reddit. (R/Liberal & R/Conservative).<br><br>Sentiment Analysis: computationally deriving the opinion from a piece of text. Positive Sentiment is indicated by higher numbers, while Negative Sentiment is indicated by lower numbers (scales from -1 - 1) <br><br> Section 1: This looks into the Word Term Frequency between the post titles of each subreddit. <br><br> Section 2: Calculates and compares the Sentiment between comments on each post.<br><br>Section 3: compares the sentiment of each 2020 of the final presidential and vice presidential candidates by each subreddit.<br><br>',
      placement = "bottom", trigger = "hover"),
      #app 
      fluidRow(class = 'Row1',align="center", style = "margin-top: 5px;",
               column(width = 4,highchartOutput("tree_lib", height = "360px")),
               column(width = 2, DT::dataTableOutput("lib_table"), style = "height:360px; overflow-y: scroll; overflow-x: scroll;"),
               column(width = 2, DT::dataTableOutput("con_table"), style = "height:360px; overflow-y: scroll; overflow-x: scroll;"),
               column(width = 4,highchartOutput("tree_cons",height = "360px"))
      ),
      
    ),
    fluidRow(class = "Row1", align = "center", style = "background-color: #FFFFFF; margin-bottom: 5px;"),
    fluidRow(class = 'Row2',align = "center",
             column(width = 2,
                fluidRow(column(2,valueBoxOutput("lm"),style = "height:120px;")),
                fluidRow(column(2,valueBoxOutput("ls"),style = "height:120px;")),
                fluidRow(column(2,valueBoxOutput("lv"),style = "height:120px;"))),
             column(width = 8, highchartOutput("dens_plot",height = "360px")),
             column(width = 2,
                fluidRow(column(2,valueBoxOutput("cm"),style = "height:120px;")),
                fluidRow(column(2,valueBoxOutput("cs"),style = "height:120px;")),
                fluidRow(column(2,valueBoxOutput("cv"),style = "height:120px")))
    ),
    fluidRow(class = "Row3", align = "center",
             h3("Sentiment Analysis Between Presidential Candidates"), style = "background-color: #4d3a7d;"),
    fluidRow(class = "Row4", align = "center", style = "background-color: #4d3a7d;",
             column(width = 3, 
                    fluidRow(column(12, div(img(src="Biden.png", height = 180, width = 180, style="border-radius: 50%; object-fit: cover;"))), align = "center"),
                    fluidRow(column(12, valueBoxOutput(width = 12, "biden_Con"),style = "height:120px; text-align: center;")),
                    fluidRow(column(12, valueBoxOutput(width = 12, "biden_lib"),style="height:120px; text-align: center;"))),
             column(width = 3,
                    fluidRow(column(12, div(img(src="Harris.png", height = 180, width = 180, style="border-radius: 50%; object-fit: cover;"))), align = "center"),
                    fluidRow(column(12, valueBoxOutput(width = 12, "kamala_con"),style="height:120px; text-align: center;")),
                    fluidRow(column(12, valueBoxOutput(width = 12, "kamala_lib"),style="height:120px; text-align: center;"))),
             column(width = 3,
                    fluidRow(column(12, div(img(src="Trump.png", height = 180, width = 180, style="border-radius: 50%; object-fit: cover;"))), align = "center"),
                    fluidRow(column(12, valueBoxOutput(width = 12, "trump_con"),style="height:120px; text-align: center;")),
                    fluidRow(column(12, valueBoxOutput(width = 12, "trump_lib"),style="height:120px; text-align: center;"))),
             column(width = 3,
                    fluidRow(column(12, div(img(src="Pence.png", height = 180, width = 180,style = "border-radius: 50%; object-fit: cover;"))), align = "center"),
                    fluidRow(column(12, valueBoxOutput(width = 12, "pence_con"),style="height:120px; text-align: center;")),
                    fluidRow(column(12, valueBoxOutput(width = 12, "pence_lib"),style="height:120px; text-align: center;")))
),
)
server <- function(input, output,session) {
    
    output$tree_lib <- renderHighchart({
      hctreemap(libs,allowDrillToNode = TRUE) %>% 
        hc_title(text = "R/Liberal Titles") %>% hc_add_theme(thm)
    })
    output$tree_cons <- renderHighchart({
      hctreemap(Conserv,allowDrillToNode = TRUE) %>% 
        hc_title(text = "R/Conservative Titles") %>% hc_add_theme(thm)
    })
    output$lib_table <- renderDT({
      lt %>% datatable(rownames = FALSE, caption = htmltools::tags$caption(
        style = 'caption-side: bottom; text-align: center; color: #FFFFFF;',
        'Table 1: ', htmltools::em('Word Term Frequency For R/Liberal')
      ),options = list(dom='t',initComplete = JS(
        "function(settings, json) {",
        "$(this.api().table().header()).css({'background-color': '#2b3e50', 'color': '#fff'});",
        "var css = document.createElement('style');
                                                        css.type = 'text/css';
                                                        css.innerHTML = '.table.dataTable.hover tbody tr:hover, table.dataTable.display tbody tr:hover { background-color: #2b3e50 !important }';
                                                        document.body.appendChild(css);",
        "}"))) %>% DT::formatStyle(columns = names(ct),backgroundColor = "#2b3e50",color ="white")
    })
    output$con_table <- renderDT({
      ct %>% datatable(rownames = FALSE, caption = htmltools::tags$caption(
        style = 'caption-side: bottom; text-align: center; color: #FFFFFF;',
        'Table 2: ', htmltools::em('Word Term Frequency For R/Conservative')
      ),options = list(dom='t',initComplete = JS(
        "function(settings, json) {",
        "$(this.api().table().header()).css({'background-color': '#2b3e50', 'color': '#fff'});",
        "var css = document.createElement('style');
                                                        css.type = 'text/css';
                                                        css.innerHTML = '.table.dataTable.hover tbody tr:hover, table.dataTable.display tbody tr:hover  { background-color: #2b3e50; !important }';
                                                        document.body.appendChild(css);",
        "}"))) %>% DT::formatStyle(columns = names(ct),backgroundColor = "#2b3e50",color ="white")
    })
    
    output$lm <- renderValueBox({
      valueBox("Sentiment Mean",
               lm)
    })
    output$ls <- renderValueBox({
      valueBox("Sentiment St. Dev",
               ls)
    })
    output$lv <- renderValueBox({
      valueBox("Sentiment Var",
               lv)
    })
    output$cm <- renderValueBox({
      valueBox("Sentiment Mean",
               cm)
    })
    output$cs <- renderValueBox({
      valueBox("Sentiment St. Dev",
               cs)
    })
    output$cv <- renderValueBox({
      valueBox("Sentiment Var",
               cv)
    })
    output$dens_plot <- renderHighchart({
      hchart(
        density(na.omit(lib_type[['sentiment']])), type = "area",
        color = "steelblue", name = "Liberal"
      ) %>% 
        hc_add_series(
          density(na.omit(cons_type[['sentiment']])), type="area",
          color = "#B71C1C", 
          name = "Conservative"
        ) %>%
        hc_title(text = "Density Plot of Sentiment Between R/Liberal and R/Conservative") %>% hc_add_theme(thm)
    })
    output$trump_con <- renderValueBox({
      valueBox("R/Conservative",
        tcc
      )
    })
    output$trump_lib <- renderValueBox({
      valueBox("R/Liberal",
        tlc
      )
    })
    output$biden_Con <- renderValueBox({
      valueBox("R/Conservative",
        bcc
      )
    })
    output$biden_lib <- renderValueBox({
      valueBox("R/Liberal",
        blc
      )
    })
    output$kamala_con <- renderValueBox({
      valueBox("R/Conservative",
        kcc
      )
    })
    output$kamala_lib <- renderValueBox({
      valueBox("R/Liberal",
        klc
      )
    })
    output$pence_con <- renderValueBox({
      valueBox("R/Conservative",
        pcc
      )
    })
    output$pence_lib <- renderValueBox({
      valueBox("R/Liberal",
        plc
      )
    })
    addTooltip(session=session,id="btn",title="Hello! This is a hover pop-up. You'll have to click to see the next one.", placement = "bottom", trigger = "hover", options = NULL)
}

shinyApp(ui = ui, server = server)