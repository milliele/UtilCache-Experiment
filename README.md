# UtilCache-Experiment

# Simulator

** Icarus 0.6.0** 

**Homepage: **[http://icarus-sim.github.io./](http://icarus-sim.github.io./)

>Saino L, Psaras I, Pavlou G. Icarus: a caching simulator for information centric networking (ICN)[C]//Proceedings of the 7th International ICST Conference on Simulation Tools and Techniques. ICST (Institute for Computer Sciences, Social-Informatics and Telecommunications Engineering), 2014: 66-75.

# Modification

* 【icarus/execution/engine.py】
    1. 新建`Strategy`对象时，如果是`POP_CACHE`策略，传入*请求生成速率*和*Zipf分布*

* 【icarus/execution/network.py】
    1. `NetworkController`增加更新到最近cache距离D和内容热度p的两个成员函数

* 【icarus/models/cache/policies.py】
    1. 增加`LCU`替换策略（使用的是旧名字`MUS`）
        1. `LCU`策略需要记录D和p，key为内容名字
        2. 需要向`NetworkModel`提供更新D和p的接口，在基类Cache里定义两个空函数，并在`MusCache`里重载函数

* 【icarus/models/strategy/onpath.py】
    1. 增加`POP_CACHE`缓存策略
    
        >Suksomboon K, Tarnoi S, Ji Y, et al. Popcache: Cache more or less based on content popularity for information-centric networking[C] Local Computer Networks (LCN), 2013 IEEE 38th Conference on. IEEE, 2013: 236-243.

    2. 增加`UTIL_CACHE`缓存策略（旧名字`MUS`）
        * 在内容返回的时候更新D
        * 每当到达下一个时间间隔，更新统计好的p

* 【icarus/scenarios/workload.py】
    1. 新增`STATIONARY_POP`
        基于`STATIONARY`修改，主要供`POP_CACHE`缓存策略使用。
        内容被分类，每类的热度分布服从Zipf，同一类内容里被请求是随机挑选的

    2. 新增`STATIONARY_FREQ`
        基于`STATIONARY`修改，主要供`UTIL_CACHE`缓存策略使用。每隔固定时间间隔会向Stategy发送事件让它更新p

    3. 新增`STATIONARY_POP_FREQ`
        基于`STATIONARY_FREQ`和`STATIONARY_POP`修改，主要供`UTIL_CACHE`缓存策略使用。每隔固定时间间隔会向Stategy发送事件让它更新p，并且内容被分类

* 【icarus/results/plot.py】
    1. 增加两个函数，分别用于在当前子图区域画出折线图和直方图

* 【icarus/results/readwrite.py】
    1. 为`ResultSet`增加函数用来剔除掉指定的实验数据
