from aws_cdk import core, aws_codepipeline as cp, aws_codepipeline_actions as cpa, aws_codecommit as cm
import permissions
class Pipeline(core.Stack):
    def __init__(self, app: core.Construct, id: str, app_name: str) -> None:
        super().__init__(app, id)
        pipeline_role = iam.LazyRole(self, 
            'PipelineRole',
            assumed_by=iam.ServicePrincipal('codepipeline.amazonaws.com')
        )
        source_action = cpa.CodeCommitSourceAction(output, repository='', trigger=None, role=None, action_name='Code Push')
        cm..Repository.fromRepositoryName(self, 'Repo')
        source_stage = cp.StageProps(
            actions=
            stage_name='SOURCE')
        Pipeline(
            self,
            app_name,
            role=pipeline_role, stages='tofillin')        