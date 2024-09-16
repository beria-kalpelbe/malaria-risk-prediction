library(foreign)
library(plm)
data <- read.csv('../../data/panel_data.csv')
pdata <- pdata.frame(data, index = c("state", "time"))

coplot(cases ~ time state, type = "l", data = pdata) 
coplot(cases ~ time | state, type = "b", data = panel)

gmm_model <- pgmm(
  cases ~ lag(cases, 1:2) + lag(t2m, 0:1) + lag(tp, 0:1) | lag(cases, 3:99) + lag(t2m, 2:99) + lag(tp, 2:99), # nolint
  data = pdata,
  effect = "individual",  # fixed effect
  model = "onestep",     # one-step GMM estimation
  transformation = "d"
)
summary(gmm_model, robust = TRUE)


# Extract the residuals from the model
resids <- residuals(gmm_model)

# Get the fixed effects by entity (average of residuals per entity)
pdata$state <- as.factor(pdata$state)  # Replace 'entity_id' with the actual entity variable
fixed_effects <- ave(resids, pdata$state)

# Print the fixed effects
print(fixed_effects)



fixed_effects <- fixef(gmm_model)
print(fixed_effects)

# Extract random effects (if applicable)
random_effects <- ranef(gmm_model)
print(random_effects)

# Extract residuals from the model
residuals <- residuals(gmm_model)
print(residuals)


# Sargan/Hansen Test
sargan_test <- sargan(gmm_model)
print(sargan_test)




# Load the package and data

dyn_model <- pgmm(cases ~ lag(cases,1) + lag(t2m,0:1) + lag(tp, 0:1) | lag(cases, 2:) + lag(t2m, 2:) + lag(tp, 2:) ,  # nolint
    data=panel, effect = 'twoways', model='twosteps', transformation = 'ld', collapse = TRUE) # nolint
summary(dyn_model, robust = TRUE)


# Estimate the dynamic model with Two-step System GMM
dyn_model <- pgmm(log(emp) ~ lag(log(emp), 1) + 
                  lag(log(wage), 0:1) + lag(log(capital), 0:1) |  # nolint
                    lag(log(emp), 2:99) + lag(log(wage), 2:99) +  # nolint
                    lag(log(capital), 2:99),
                  data = EmplUK,  # nolint
                  effect = "twoways",
                  model = "twosteps",
                  transformation = "ld",
                  collapse = TRUE
)





library(plm)
fixed <- plm(cases ~ t2m + tp, data=pdata, index=c("state", "time"), model="within")  #fixed model
random <- plm(cases ~ t2m + tp, data=pdata, index=c("state", "time"), model="random")  #random model
phtest(fixed,random) #Hausman test


fixef(fixed)


# simple OLS regression
ols <-lm(cases ~ t2m + tp, data=panel)
summary(ols) 

# OLS vs. fixed effects
pFtest(fixed, ols)