from i2b2tools.lib.standoff_annotations import EvaluatePHI

class PostProcessor(object):
    processors = []
    evaluator = EvaluatePHI
    system_sas = []
    gold_sas = []
    pre_evaluation_score = 0.0
    post_evaluation_score = 0.0

    def __init__(self, system_sas, gold_sas, processors=[], evaluator=EvaluatePHI):
        self.system_sas = system_sas
        self.gold_sas = gold_sas
        self.processors += processors
        self.evaluator = evaluator

        e = self.evaluator(self.system_sas, self.gold_sas)
        self.pre_evaluation_score = e.F_beta(e.micro_precision(),
                                             e.micro_recall())

    def process(self):
        for (rule, args) in self.processors:
            for sa in self.system_sas.values():
                args_with_sa = [sa] + args
                rule(*args_with_sa).apply()

        e = self.evaluator(self.system_sas, self.gold_sas)
        self.post_evaluation_score = e.F_beta(e.micro_precision(),
                                              e.micro_recall())

    def summary(self):
        print "%.2f -> %.2f" % (self.pre_evaluation_score,
                                self.post_evaluation_score)
