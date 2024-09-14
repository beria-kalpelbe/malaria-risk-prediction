library(foreign)
# Panel <- read.dta("http://dss.princeton.edu/training/Panel101.dta")
panel <- read.csv('../../data/panel_data.csv')
coplot(cases ~ time|state, type="l", data=panel)
coplot(cases ~ time|state, type="b", data=panel)

library(plm)
fixed <- plm(cases ~ t2m + tp, data=panel, index=c("state", "time"), model="within")  #fixed model
random <- plm(cases ~ t2m + tp, data=panel, index=c("state", "time"), model="random")  #random model
phtest(fixed,random) #Hausman test


fixef(fixed)


# simple OLS regression
ols <-lm(cases ~ t2m + tp, data=panel)
summary(ols) 

# OLS vs. fixed effects
pFtest(fixed, ols)