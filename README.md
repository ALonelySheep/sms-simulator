# SMS Simulator

## Overview

The SMS Simulator is a program designed to simulate the sending of SMS messages with varying parameters, sender configurations, and monitor their progress in real-time.

## Project Structure

```terminal
root
│
├── src/                    # Source files for the core application
│   ├── __init__.py         
│   ├── producer.py         # Contains the MessageProducer class
│   ├── sender.py           # Contains the MessageSender class
│   └── monitor.py          # Contains the ProgressMonitor class
│
├── tests/                  # Unit tests
│   ├── __init__.py       
│   ├── test_producer.py    # Tests for message producer functionality
│   ├── test_sender.py      # Tests for message sender functionality
│   └── test_monitor.py     # Tests for progress monitor functionality
│
├── config/                 
│   └── settings.json       # Configuration file for adjusting simulation parameters
│
├── .gitignore              
├── environment.txt         # Project's dependency list
├── README.md               # This file; project overview and instructions
└── main.py                 # Main entry point for the simulation
```

## Setup

### Environment Setup

To recreate the environment for this project:

Using the `.txt` file:

```bash
conda create --name sms --file environment.txt
```

Using the `.yml` file:

```bash
conda env create -f environment.yml
```

### Launching the Project

Configure the simulation by editing the `config/settings.json`:

```json
{
    "message_count": 400000,
    "update_interval": 1,
    "senders": [
        {
            "mean_wait_time": 0.1,
            "failure_rate": 0.02,
            "quantity": 100
        },
        {
            "mean_wait_time": 0.2,
            "failure_rate": 0.001,
            "quantity": 800
        }
    ],
    "resend_failed_msg": false,
    "max_resend_attempts": 3
}
```

Start the simulation:

```bash
python ./main.py
```

During execution, the monitor will provide real-time updates:

```bash
[Progress Monitor] (00:01:14)
 Messages sent: 371830
 Messages failed: 19558 (5.00%)
 Average time per message: 0.000191 seconds
```

Interrupt the program at any point with `Ctrl + C`.

## Testing

To run unit tests for the entire project:

```bash
python -m unittest
```

Sample successful test output:

```bash
...............
----------------------------------------------------------------------
Ran 15 tests in 0.010s

OK
```

For individual class testing:

```bash
python -m unittest tests.[FileName]
# Example:
python -m unittest tests.test_monitor
```

## Improved Features

### Structured as a Python Package

The SMS Simulator is developed as a Python package, enhancing the organization and maintainability of the code. This approach allows for a clear hierarchical directory structure, reducing the likelihood of naming conflicts and facilitating easy imports. It also offers modularity, paving the way for modules to be reused in future projects seamlessly.

### Realistic Timing with Exponential Distribution

To realistically simulate the timing of message sending, the simulator employs an exponential distribution. This choice is informed by the need to replicate real-world operational unpredictability, where each message's send time is independent, mimicking the variability caused by server loads and network latency. By tweaking the mean parameter, the simulator can effectively model a range of sender behaviors, thereby providing a more accurate representation of actual conditions.

### Graceful Program Termination

Ensuring the simulator can terminate smoothly was a priority. Standard interruption commands like Ctrl + C often leave the main thread in a wait state. To address this, the simulator is designed to capture the KeyboardInterrupt exception within the main thread and signal all child threads to conclude their operations. This mechanism allows for a controlled and graceful shutdown, preventing hang-ups and ensuring clean exits.
