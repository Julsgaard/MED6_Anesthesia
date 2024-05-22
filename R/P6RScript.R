#------- Libraries -------
library(tidyverse)
library(readbulk)
library(magrittr)
library(ggpubr)
library(reshape2)
library(Hmisc)
library(pastecs)
library(FSA)
library(ggplot2)
library(readr)
library(dplyr)
library(ggpmisc)
library(gridExtra)
#----- Mouth Opening -----
# Calculate Pearson and Spearman correlation coefficients
pearson_cor <- cor(MouthOpeningData$`Measured.mouth.height..cm.`, MouthOpeningData$`System.mouth.height..Percentage.increase.`, method = "pearson")
spearman_cor <- cor(MouthOpeningData$`Measured.mouth.height..cm.`, MouthOpeningData$`System.mouth.height..Percentage.increase.`, method = "spearman")

# Print the correlation coefficients
print(paste("Pearson Correlation Coefficient:", pearson_cor))
print(paste("Spearman Correlation Coefficient:", spearman_cor))

# Plot: Correlation between Measured Mouth Height and System Mouth Height Increase with Linear Regression
ggplot(MouthOpeningData, aes(x = `Measured.mouth.height..cm.`, y = `System.mouth.height..Percentage.increase.`)) +
  geom_point(color = 'blue') +
  geom_smooth(method = 'lm', col = 'red') +
  labs(title = "Correlation between Measured Mouth Height and System Mouth Height",
       subtitle = paste("Pearson Correlation:", round(pearson_cor, 2), "Spearman Correlation:", round(spearman_cor, 2)),
       x = "Measured Mouth Height (cm)",
       y = "System Mouth Height Increase (%)")



# Your existing data and plot with adjusted x-axis and regression line
ggplot(MouthOpeningData, aes(x = `Measured.mouth.height..cm.`, y = `System.mouth.height..Percentage.increase.`)) +
  geom_point(color = 'blue') +
  geom_smooth(method = 'lm', col = 'red', fullrange = TRUE) +  # Ensure the regression line covers the full range
  labs(
    title = "Correlation between Measured Mouth Height and System Mouth Height",
    subtitle = paste("Pearson Correlation:", round(pearson_cor, 2), "Spearman Correlation:", round(spearman_cor, 2)),
    x = "Measured Mouth Height (cm)",
    y = "System Mouth Height Increase (%)"
  ) +
  scale_x_continuous(limits = c(0, max(MouthOpeningData$`Measured.mouth.height..cm.`)))

# Your existing data and plot with adjusted axis scales and breaks
ggplot(MouthOpeningData, aes(x = `Measured.mouth.height..cm.`, y = `System.mouth.height..Percentage.increase.`)) +
  geom_point(color = 'blue') +
  geom_smooth(method = 'lm', col = 'red', fullrange = TRUE) +  # Ensure the regression line covers the full range
  labs(
    title = "Correlation between Measured Mouth Height and System Mouth Height",
    x = "Measured Mouth Height (cm)",
    y = "System Mouth Height Increase (%)"
  ) +
  scale_x_continuous(limits = c(0, max(MouthOpeningData$`Measured.mouth.height..cm.`)), breaks = seq(0, max(MouthOpeningData$`Measured.mouth.height..cm.`), by = 1)) +
  scale_y_continuous(breaks = seq(0, max(MouthOpeningData$`System.mouth.height..Percentage.increase.`), by = 500))

# best one yet
# Your existing data and plot with adjusted axis scales and breaks
ggplot(MouthOpeningData, aes(x = `Measured.mouth.height..cm.`, y = `System.mouth.height..Percentage.increase.`)) +
  geom_point(color = 'blue') +
  geom_smooth(method = 'lm', col = 'red', fullrange = TRUE) +  # Ensure the regression line covers the full range
  labs(
    title = "Correlation between Measured Mouth Height and System Mouth Height",
    x = "Measured Mouth Height (cm)",
    y = "System Mouth Height Increase (%)"
  ) +
  scale_x_continuous(limits = c(0, max(MouthOpeningData$`Measured.mouth.height..cm.`, na.rm = TRUE)), 
                     breaks = seq(0, max(MouthOpeningData$`Measured.mouth.height..cm.`, na.rm = TRUE), by = 1)) +
  scale_y_continuous(breaks = seq(0, max(MouthOpeningData$`System.mouth.height..Percentage.increase.`, na.rm = TRUE), by = 500))

#----- Neck Movement ------
#Plot
ggplot(NeckMovementData, aes(x = `Participant Number`, y = Error)) +
  #geom_line(aes(y = `Amount overshot`), color = 'red', size = 1) +
  geom_point(color = 'black', size = 2) +
  geom_hline(yintercept = 0, linetype = "dashed", color = "blue") +
  labs(title = "Error between System prediction and Observed value",
       x = "Participant Number",
       y = "Error (System prediction - Observed value)") +
  theme(legend.position = "none")

#Stats
NeckMovementStats <- NeckMovementData %>%
  summarise(
    `System prediction mean` = mean(`System.prediction`),
    `System prediction median` = median(`System.prediction`),
    `System prediction sd` = sd(`System.prediction`),
    `System prediction IQR` = IQR(`System.prediction`),
    `Observed value mean` = mean(`Observed.value`),
    `Observed value median` = median(`Observed.value`),
    `Observed value sd` = sd(`Observed.value`),
    `Observed value IQR` = IQR(`Observed.value`),
    `Amount overshot mean` = mean(`Amount.overshot`),
    `Amount overshot median` = median(`Amount.overshot`),
    `Amount overshot sd` = sd(`Amount.overshot`),
    `Amount overshot IQR` = IQR(`Amount.overshot`)
  )

# Convert the data to long format for easier plotting
NeckMovementData_long <- NeckMovementData %>%
  gather(key = "Type", value = "Value", `Amount.overshot`, `Backtilt.Overshoot`, `Forwardtilt.Overshoot`)

# Rename the levels for the x-axis
NeckMovementData_long$Type <- factor(NeckMovementData_long$Type, 
                                     levels = c("Amount.overshot", "Backtilt.Overshoot", "Forwardtilt.Overshoot"),
                                     labels = c("Total Tilt", "Back Tilt", "Forward Tilt"))

# Boxplot for Amount overshot, Backtilt overshoot, and Forward tilt overshoot with customized axis labels and text size
ggplot(NeckMovementData_long, aes(x = Type, y = Value, fill = Type)) +
  geom_boxplot(aes(color = Type), alpha = 0.5) +  # Add transparency to the boxplots
  geom_point(size = 2, position = position_jitter(width = 0.15)) +
  #scale_color_manual(values = c("Total" = "red", "Back Tilt" = "green", "Forward Tilt" = "blue")) +
  labs(
    x = "",
    y = "Amount of Degrees Overshot") +
  theme(legend.position = "none",
        axis.text.x = element_text(size = 15),
        axis.text.y = element_text(size = 15),
        axis.title.y = element_text(size = 15),
        plot.title = element_text(size = 16))

# Scatterplot for Amount overshot, Backtilt overshoot, and Forward tilt overshoot
ggplot(NeckMovementData_long, aes(x = Type, y = Value, color = Type)) +
  geom_point() +
  labs(title = "Scatterplot of Amount Overshot, Backtilt Overshoot, and Forward Tilt Overshoot",
       x = "Type",
       y = "Value") +
  theme(legend.position = "none")
