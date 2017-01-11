# Compare UtilCache with Benchmark Stratigies

**Benchmark: ** LCE, HR Symm, ProbCache, PopCache

## Run
To run the expriments and plot the results, execute the `run.sh` script:

    $ sh run.sh

## 实验设计
总共进行3类实验：

1. A和C固定时，研究不同拓扑下，不同时间间隔对UtilCache性能（Cache Hit Ratio和Latency）的影响
2. A和时间间隔都固定时，研究不同拓扑下，不同C对UtilCache性能（Cache Hit Ratio和Latency）的影响
3. C和时间间隔都固定时，研究不同拓扑下，不同A对UtilCache性能（Cache Hit Ratio和Latency）的影响


## 文档
### config.py
用于设计实验
### plotresults.py
用于给实验结果画图
### removeresult.py
用于删除指定实验结果里的部分数据
