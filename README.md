# Kubernetes deployment

### Step 1: Install Minikube and Kubectl

1. **Install Minikube**
   - Follow the [official installation guide](https://minikube.sigs.k8s.io/docs/start/) to install Minikube on your operating system.

2. **Install Kubectl**
   - Follow the [official installation guide](https://kubernetes.io/docs/tasks/tools/install-kubectl/) to install `kubectl`, the command-line tool for Kubernetes.

### Step 2: Start Minikube

Start Minikube with the desired driver (e.g., `docker`):

```bash
minikube start --driver=docker
```

### Step 3: Create Docker Images

Since Minikube runs its own Docker daemon, you need to build your Docker images within the Minikube environment.

1. **Set Docker environment to Minikube**
   ```bash
   eval $(minikube -p minikube docker-env)
   ```

2. **Build Docker images**
   ```bash
   docker-compose build
   ```

### Step 4: Create Kubernetes Manifests

Create Kubernetes YAML files for deployment and service configuration.

1. **Create a directory for Kubernetes manifests**
   ```bash
   mkdir k8s
   cd k8s
   ```

2. **Create MySQL Deployment and Service**

   Create a file named `mysql-deployment.yml`:
   ```yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: mysql
   spec:
     selector:
       matchLabels:
         app: mysql
     strategy:
       type: Recreate
     template:
       metadata:
         labels:
           app: mysql
       spec:
         containers:
         - image: mysql:5.7
           name: mysql
           env:
           - name: MYSQL_ROOT_PASSWORD
             value: root
           - name: MYSQL_DATABASE
             value: test_db
           ports:
           - containerPort: 3306
             name: mysql
           volumeMounts:
           - name: mysql-persistent-storage
             mountPath: /var/lib/mysql
         volumes:
         - name: mysql-persistent-storage
           persistentVolumeClaim:
             claimName: mysql-pv-claim
   ---
   apiVersion: v1
   kind: Service
   metadata:
     name: mysql
   spec:
     ports:
     - port: 3306
     selector:
       app: mysql
   ```

   Create a file named `mysql-pv.yml`:
   ```yaml
   apiVersion: v1
   kind: PersistentVolume
   metadata:
     name: mysql-pv
   spec:
     capacity:
       storage: 1Gi
     accessModes:
       - ReadWriteOnce
     hostPath:
       path: "/mnt/data"
   ---
   apiVersion: v1
   kind: PersistentVolumeClaim
   metadata:
     name: mysql-pv-claim
   spec:
     resources:
       requests:
         storage: 1Gi
     accessModes:
       - ReadWriteOnce
   ```

3. **Create Flask Deployment and Service**

   Create a file named `flask-deployment.yml`:
   ```yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: flask-app
   spec:
     selector:
       matchLabels:
         app: flask-app
     template:
       metadata:
         labels:
           app: flask-app
       spec:
         containers:
         - name: flask-app
           image: flask_mysql_docker_web:latest
           ports:
           - containerPort: 5000
           env:
           - name: FLASK_ENV
             value: development
           - name: DB_HOST
             value: mysql
           - name: DB_USER
             value: root
           - name: DB_PASSWORD
             value: root
           - name: DB_NAME
             value: test_db
   ---
   apiVersion: v1
   kind: Service
   metadata:
     name: flask-app
   spec:
     type: NodePort
     ports:
     - port: 5000
       nodePort: 30007
     selector:
       app: flask-app
   ```

### Step 5: Apply Kubernetes Manifests

Apply the Kubernetes manifests to create the deployments and services.

1. **Apply Persistent Volume and MySQL Deployment**
   ```bash
   kubectl apply -f mysql-pv.yml
   kubectl apply -f mysql-deployment.yml
   ```

2. **Apply Flask Deployment**
   ```bash
   kubectl apply -f flask-deployment.yml
   ```

### Step 6: Verify Deployment

Check the status of your deployments and services.

1. **Get the list of pods**
   ```bash
   kubectl get pods
   ```

2. **Get the list of services**
   ```bash
   kubectl get services
   ```

### Step 7: Access the Flask Application

Since the Flask service is exposed as a `NodePort`, you can access it via the Minikube IP and the node port.

1. **Get Minikube IP**
   ```bash
   minikube ip
   ```

2. **Access the application**
   Open your browser and navigate to `http://<minikube-ip>:30007`.

### Step 8: Testing the API

Use `curl` or Postman to test the API endpoints.

1. **Add a new user**
   ```bash
   curl -X POST -H "Content-Type: application/json" -d "{\"name\": \"John Doe\", \"email\": \"john@example.com\"}" http://<minikube-ip>:30007/users
   ```

2. **Get all users**
   ```bash
   curl http://<minikube-ip>:30007/users
   ```

By following these steps, you should be able to deploy your Flask application with MySQL to Kubernetes using Minikube.