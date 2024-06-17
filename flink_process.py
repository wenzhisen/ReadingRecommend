import happybase
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.functions import MapFunction
from datetime import datetime
import re
# 定义一个将数据写入 HBase 的 SinkFunction
class HBaseSink:
    def __init__(self, table_name):
        self.table_name = table_name

    def open(self, parameters):
        self.connection = happybase.Connection('10.242.16.254',port=9090)  # 修改为你的 HBase 配置
        self.table = self.connection.table(self.table_name)

    def invoke(self, value):
        row_key = datetime.now().strftime("%Y%m%d%H%M%S%f")
        data=value
        self.table.put(row_key.encode('utf-8'), {b'cf:q1': data.encode('utf-8')})

    def close(self):
        self.connection.close()

# 自定义 MapFunction 来处理输入数据
class MyMapFunction(MapFunction):
    def map(self, value):
        value = re.sub(r'\s|\W', '', value)
        # 去除表情包
        value = re.sub(r'[\U00010000-\U0010ffff]', '', value)
        return value

# 设置执行环境
env = StreamExecutionEnvironment.get_execution_environment()

# 创建一个数据流
data_stream = env.read_text_file("/path/to/your/directory/*.txt")# 替换为你的数据文件路径

# 使用 MapFunction 转换数据
mapped_stream = data_stream.map(MyMapFunction())

# 添加 HBase Sink
mapped_stream.add_sink(HBaseSink('my_table'))  # 替换为你的 HBase 表名

# 执行作业
env.execute("Flink to HBase")