# helics\_benchmark\_results
Repo containing [HELICS](www.github.com/GMLC-TDC/HELICS) benchmark results and processing code for the results

## Slightly Helpful Benchmark Explanations
+ *ActionMessage* and *Conversion* are purely testing specific functions and activities and contain no scaling.
 
+ *echo* and *echoMessage* test a single root federate that is responding to leaf federates with values or messages. The number surrounded by "/" is the number of leaf federates sending messages.

+ *FilterBenchmarks* has two numbers the first is the number of federates, it is a variant on echoMessage,  the second number 0 or 1 is a flag (1=source filter, 0=destination filter)
 
+ *messageLookup* constructs a federation that randomly sends messages between its members. The first value surrounded by "/" in the benchmark name is the total number of interfaces across all federation members. The second surrounded value is the total number of federates

 
+ *messageSend* is a federation with two members. The first "/" surrounded value in the benchmark name is the size of the message being sent and the second is the number of messages being sent.
 
+ *ringBenchmarks* is a federation where the federate interfaces are assembled in a ring and a chunk of data is passed through the federation a fixed number of times. The value surrounded by "/" in the benchmark name is the number of federates.

 
+ *phold* runs the pHOLD benchmark

## Release
HELICS and helics_benchmark_results are distributed under the terms of the BSD-3 clause license. All new
contributions must be made under this license. [LICENSE](LICENSE)

SPDX-License-Identifier: BSD-3-Clause
