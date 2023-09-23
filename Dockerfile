FROM public.ecr.aws/lambda/python:3.11

# Copy function code
COPY willkronberg /asset/willkronberg

# Install the function's dependencies using file requirements.txt
# from your project folder.
COPY .venv venv
RUN . venv/bin/activate

COPY requirements.txt  .
RUN  python -m pip install -r requirements.txt --target /asset --disable-pip-version-check

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "willkronberg.app.lambda_handler" ]