# RotorHazard Class Rank Best Percentage
"Best Percentage of Rounds" class ranking plugin for RotorHazard

## Installation

Copy the `class_rank_best_pct_rounds` plugin into the `src/server/plugins` directory in your RotorHazard install. Start RotorHazard.

If installation is successful, the RotorHazard log will contain the message `Loaded plugin module class_rank_best_pct_rounds` at startup.

## Usage

After creating a class, select "Laps/Time: Best % Rounds" for the class ranking method. Using the settings button, enter your rounds percentage and choose whether to round up, down, or to the nearest value.

### Example

7 rounds have been run and the plugin's `percentage` set to 60.

With `rounding` set to `Down`: 4 rounds are included
With `rounding` set to `Nearest`: 4 rounds are included
With `rounding` set to `Up`: 5 rounds are included