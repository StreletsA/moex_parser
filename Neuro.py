from numpy import exp, array, random, dot

from MoexDataWorker import MoexDataWorker

# Переписать, чтобы тесты составлялись из всех цен в таблице sec_id
def create_learn_data(sec_id, inputs_count=4, tests_count=5, delta=5):
    mdw = MoexDataWorker()
    count = inputs_count + 1 + delta
    data = mdw.get_stock_info(sec_id)[1:]  # ('2012-04-11', '5307')
    tests_inputs = []
    tests_outputs = []
    test_data = []

    pos = 0
    for i in range(tests_count):
        tmp = []
        stop = False
        j = pos
        while j < pos + count:
            try:
                if data[j][1] == None:
                    pos += 1
                    j += 1
                    continue
                price = float(data[j][1])
                tmp.append(price)
                j += 1
            except IndexError:
                stop = True
                break
        if stop:
            break

        pos += 1
        tests_inputs.append(tmp)

    c = 0
    for i in tests_inputs:
        tmp = []
        start_price = i[0]
        for j in i[1:]:
            if j > start_price:
                tmp.append(1)
            else:
                tmp.append(0)

        tests_inputs[c] = tmp[:inputs_count]

        ans = tmp[len(tmp)-1]
        tests_outputs.append(ans)

        c += 1

    test_data = [tests_inputs, tests_outputs]

    return test_data

def del_nonetypes(arr):
    ans = []
    for i in arr:
        if not i == None:
            ans.append(i)
    return ans

def create_question(sec_id, inputs_count):
    mdw = MoexDataWorker()
    all_data = del_nonetypes([x[1] for x in mdw.get_stock_info(sec_id)[1:]])

    data = all_data[len(all_data)-inputs_count-1:]
    start_price = 0
    try:
        start_price = float(data[0])
    except:
        d = [x[1] for x in mdw.get_stock_info(sec_id)[1:]]
        s = len(data)-inputs_count-2
        while d[s] == None and s >= 0:
            s -= 1

        if d[s] == None:
            return

        start_price = float(d[s])

    question_arr = []

    for i in data[1:]:
        if float(i) > start_price:
            question_arr.append(1)
        else:
            question_arr.append(0)

    return question_arr


def get_prediction(sec_id, input=None, inputs_count=19, training_tests_count=150, epochs=35000):
    if not input == None:
        inputs_count = len(input)
    n = Neuron(inputs_count)
    learn_data = create_learn_data(sec_id, inputs_count, training_tests_count)

    n.train(array(learn_data[0]), array([learn_data[1]]).T, epochs)

    return n.think(array(create_question(sec_id, inputs_count)))



def create_training_inputs():
    pass

def create_training_outputs():
    pass

class Neuron():
    def __init__(self, inputs_count=3, outputs_count=1):
        random.seed(1)

        self.inputs_count = inputs_count
        self.outputs_count = outputs_count

        # 3 inputs and 1 output
        self.synaptic_weights = 2 * random.random((inputs_count, outputs_count)) - 1

    def __sigmoid(self, x):
        return 1 / (1 + exp(-x))

    def __sigmoid_derivative(self, x):
        return x * (1 - x)

    def train(self, training_set_inputs, training_set_outputs, number_of_training_iterations):
        for iteration in range(number_of_training_iterations):
            output = self.think(training_set_inputs)

            error = training_set_outputs - output
            #print(error)
            adjustment = dot(training_set_inputs.T, error * self.__sigmoid_derivative(output))

            self.synaptic_weights = self.synaptic_weights + adjustment

    def think(self, inputs):
        return self.__sigmoid(dot(inputs, self.synaptic_weights))