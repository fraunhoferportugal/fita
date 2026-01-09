---
sidebar_position: 1
---
# Create embServe Workload

Services to be deployed in Far-Edge devices powered by embServe can be generated using C code. For that, an SDK is provided by embServe, which services must use to ensure compatibility. This page details a simple example showing how this process works.

## embServe SDK Setup

The SDK includes everything needed to generate embServe-compliant files. To setup the SDK:

1. Download the SDK bundle from [here](/res/embserve/embservesdk-1.0.2-e4c86f8@afe44f089b7.zip)

2. Unzip file
```shell
unzip embservesdk-*.zip -d embserve-sdk
```

3. Setup Python venv
```shell
cd embserve-sdk
python3 -m venv .venv
. .venv/bin/activate
```

4. Setup the toolchain
```shell
./setup_toolchain.sh
```

5. Export the toolchain path as instructed by the setup script. As an example:
```shell
export ZEPHYR_SDK_PATH=/home/user/Workspace/embserve-sdk/toolchain/zephyr/zephyr-sdk-0.16.1
```

6. Add the folder `embserve-sdk/toolchain/udynlink-ng` to the PATH. As an example:

```shell
export PATH=/home/user/Workspace/embserve-sdk/toolchain/udynlink-ng:$PATH
```

:::note
You need to run the commands above every time you open a new shell. To prevent this, you can add them to the end of your ~/.bashrc or ~/.profile
:::

7. Validate the mkmodule command is available:

```shell
mkmodule --help
```

## Creating an embServe Service

1. Create a folder inside the `embserve-sdk/` folder

```shell
cd embserve-sdk
mkdir service
```

2. Create the file service.c in the `embserve-sdk/` folder with the following:

```c
#include "../include/embserve.h"
#include <string.h>
#include <stdio.h>


static bool running = false;
static int delay_ms;

int setup(void) {
    printf("%s started!", SERVICE_NAME);
    running = true;
    delay_ms = 30000;
    return 0;
}

void loop(void) {
    printf("Loop");

    embserve_sensor_data_t sensor_data = {0};
    int sensor_id = 0;

    while(running) {
        int res = embserve_get_sensor(SENSOR_TEMPERATURE, &sensor_id);
        if(res < 0) {
            printf("Failed to get sensor!");
            return;
        }

        res = embserve_get_sensor_data(sensor_id, &sensor_data);
        if(res < 0) {
            printf("Failed to get sensor data!");
            return;
        }

        embserve_io_t output = {
            .key = "value",
            .type = EMBSERVE_FLOAT,
            .data_len = 1,
            .data = sensor_data.values
        };
        embserve_output(&output);
        sleep(delay_ms);
    }
}

void on_input(embserve_io_t * input) {
    if(strcmp(input->key, "rate") == 0) {
        int new_delay_ms = *(int *)input->data;
        if(new_delay_ms < 1000) {
            printf("on_input(): Bad input. Rate too low (%d)", new_delay_ms);
            return;
        }

        delay_ms = new_delay_ms;
        printf("on_input(): New rate %d ms", delay_ms);
    }
}

void on_quit(void) {
    running = false;
}
```

:::info
This service collects Temperature data and sends it as an output ("value"). The sample rate is configurable with the input "rate".
:::

3. Build the service:

```shell
mkmodule service.c ../src/*.c --name temperature_sensor
```

4. Get the base64 of the generated binary

```shell
base64 temperature_sensor.bin -w 0
```

5. Create the JSON manifest, `service.json`. Replace `<service binary in base64>` with the output of the previous command :

```json
{
    "name": "temperature_sensor",
    "version": 1,
    "service": <service binary in base64>,
    "dependencies": {
        "sdk_api": 1
    },
    "inputs": [
        {
            "key": "rate",
            "type": 0
        }
    ],
    "outputs": [
        {
            "key": "value",
            "type": 1
        }
    ]
}
```

:::warning
The inputs and outputs section must match your service. Any output or input not matching the manifest will be discarded by embServe! 
:::

6. Service manifest is now ready to be deployed

For more information about embServe and its services, refer to [this](https://ieeexplore.ieee.org/document/10144123) article.

Refer to [Deploy Workloads on Far-edge Devices](../getting-started/workloads.md) to learn how to deploy this service using FITA.
