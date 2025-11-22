lenovo@raspberrypi5:~/scrimba/floodsight $ kubectl get pods -n floodsight
NAME                                    READY   STATUS    RESTARTS   AGE
floodsight-backend-788748f66d-c97xs     1/1     Running   0          53m
floodsight-backend-788748f66d-rhr4c     1/1     Running   0          53m
floodsight-scheduler-74b7954888-8rnt4   1/1     Running   0          53m
postgres-0                              1/1     Running   0          57m
lenovo@raspberrypi5:~/scrimba/floodsight $ kubectl get svc -n floodsight
NAME                          TYPE           CLUSTER-IP      EXTERNAL-IP   PORT(S)                      AGE
floodsight-backend            ClusterIP      10.43.68.71     <none>        8080/TCP                     2m4s
floodsight-backend-external   LoadBalancer   10.43.229.84    <pending>     80:30636/TCP,443:31923/TCP   2m4s
postgres                      ClusterIP      10.43.185.107   <none>        5432/TCP                     65m