export WORKSPACE_LOCATION = ${PWD}

.PHONY: help
help:          ## Show help messages and exit.
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'


.PHONY: pull
pull:          ## pull the aws glue docker image from docker hub
	docker pull amazon/aws-glue-libs:glue_libs_3.0.0_image_01

.PHONY: jupyter
jupyter:       ## run a jupyter notebook server in the aws glue docker container
	docker run -it -v ~/.aws:/home/glue_user/.aws \
		-v ${WORKSPACE_LOCATION}:/home/glue_user/workspace/jupyter_workspace/ \
		-e AWS_REGION=eu-central-1 \
		-e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
		-e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
		-e AWS_SESSION_TOKEN=${AWS_SESSION_TOKEN} \
		-e AWS_SECURITY_TOKEN=${AWS_SECURITY_TOKEN} \
		-e AWS_SESSION_EXPIRATION=${AWS_SESSION_EXPIRATION} \
		-e DISABLE_SSL=true \
		--rm -p 4040:4040 -p 18080:18080 -p 8998:8998 -p 8888:8888 \
		--name glue_jupyter_lab amazon/aws-glue-libs:glue_libs_3.0.0_image_01 /home/glue_user/jupyter/jupyter_start.sh

.PHONY: test
test:          ## run tests using pytest in the aws glue docker container
	docker run -it -v ~/.aws:/home/glue_user/.aws \
		-v ${WORKSPACE_LOCATION}:/home/glue_user/workspace/ \
		-e AWS_PROFILE=${PROFILE_NAME} \
		-e WORKSPACE_LOCATION=${WORKSPACE_LOCATION} \
		-e DISABLE_SSL="true" \
		--rm --name glue_pytest amazon/aws-glue-libs:glue_libs_3.0.0_image_01 -c "python3 -m pytest tests -vv -s"

.PHONY: bash
bash:          ## get a bash prompt in the glue container
	docker run -it -v ~/.aws:/home/glue_user/.aws \
		-v ${WORKSPACE_LOCATION}:/home/glue_user/workspace/ \
		-e AWS_PROFILE=${PROFILE_NAME} \
		-e WORKSPACE_LOCATION=${WORKSPACE_LOCATION} \
		-e DISABLE_SSL="true" \
		--rm --name glue_pytest amazon/aws-glue-libs:glue_libs_3.0.0_image_01 -c "/bin/bash"

.PHONY: gluezip
gluezip:       ## download the aws glue source code to add as a reference to your project for autocomplete
	curl https://s3.amazonaws.com/aws-glue-jes-prod-us-east-1-assets/etl-3.0/python/PyGlue.zip --output tools/pyglue.zip


.PHONY: glue
glue:          ## clone AWS glue source code and copy it into venv for autocomplete to work.
	cd tools \
	&& rm -rf aws-glue-libs \
	&& git clone git@github.com:awslabs/aws-glue-libs.git \
	&& cd .. \
	&& cp -r ./tools/aws-glue-libs/awsglue ./venv/lib/python*/site-packages \
	&& rm -rf tools/aws-glue-libs
