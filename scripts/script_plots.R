library(dplyr)
library(ggplot2)

ggplot(data, aes(x = n_distance_classes, y = n_luminance_classes)) +
  geom_point(size = 3, color="black") +
  geom_line(, color="black") +
  labs( 
    title = "Relação entre o Número de Classes de Distância e o Número de Classes de Luminância",
    x = "Número de Classes de Distância",
    y = "Número de Classes de Luminância") +
  theme_minimal() +
  scale_x_continuous(
    breaks = seq(min(data$n_distance_classes), max(data$n_distance_classes), by = 1),  # Intervalos de 0.5 no eixo X
    labels = scales::number_format()) +

  scale_y_continuous(
    breaks = seq(min(data$n_luminance_classes), max(data$n_luminance_classes), by = 1),  # Intervalos de 0.5 no eixo Y
    labels = scales::number_format()) +
  theme(
    plot.title = element_text(hjust = 0.5, size = 12, face = "bold"),
    axis.text.x = element_text(size = 12),
    axis.text.y = element_text(size = 12),
    legend.position = "none")

full_painting_data <- full_join(general_group_data, painting_data, by = "group_and_title")

ggplot(general_distance_data, aes(x = mean_luminance, y = distance_class)) +
  geom_point(color = "blue", size = 1) +
  labs(
    title = "Relação entre Luminância Média e Classes de Distância",
    x = "Luminância Média",
    y = "Classes de Distância") +
  theme_minimal() +
  theme(plot.title = element_text(hjust = 0.5, size = 12, face = "bold")) +
  scale_x_continuous(
    breaks = seq(0, max(general_distance_data$mean_luminance), by = 0.05)) +
  scale_y_continuous(
    breaks = seq(0, 3, by = 0.1))
  
ggplot(general_luminance_data, aes(x = mean_distance, y = luminance_class)) +
  geom_point(color = "blue", size = 1) +
  labs(
    title = "Relação entre Distância Média e Classes de Luminância",
    x = "Distância Média",
    y = "Classes de Luminância") +
  theme_minimal() +
  theme(
    plot.title = element_text(hjust = 0.5, size = 12, face = "bold")) +
  scale_x_continuous(
    breaks = seq(0, max(general_luminance_data$mean_distance), by = 0.3)) +
  scale_y_continuous(
    breaks = seq(0, 1, by = 0.05))

cor.test(general_luminance_data$mean_distance, general_luminance_data$luminance_class, method="spearman")
cor.test(general_distance_data$mean_luminance, general_distance_data$distance_class, method="spearman")
