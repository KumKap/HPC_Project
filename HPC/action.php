<?php
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_FILES['myfile']['name'])) {
       
            $path = 'C:/xampp/htdocs/HPC/HPC_Project/';
            $file_name = $_FILES['myfile']['name'];
            $file_tmp = $_FILES['myfile']['tmp_name'];
            $temp = (explode('.', $_FILES['myfile']['name']));
            $file_ext = strtolower(end($temp));
            $file = $path . $file_name;
            move_uploaded_file($file_tmp, $file);
            $clusters = $_POST['cluster'];
            $head = $_POST['head'];
            $proc = $_POST['proc'];
            $output = "";
            
            if($file_ext == "xlsx" or $file_ext == "csv") {
                // $cmd = "cd C:/Users/KumKap/PycharmProjects/BE/HPC_Project"; 
                // $output = shell_exec ($cmd);
                $cmd = "mpiexec -n $proc python -m mpi4py C:/xampp/htdocs/HPC/HPC_Project/kmeans2.py".
                " $file $clusters $file_ext $head";
                $output = shell_exec ($cmd);
                //echo $cmd2;
                //echo $output2;
                $result = json_decode($output, true);
                $avg_time = $result["avg_time"];
                $max_time = $result["max_time"];
                $avg_time = $avg_time / 2.70400194262;
                $max_time = $max_time / 2.70400194262;
                $centroid_x = $result['centroid_x'];
                $centroid_x = trim($centroid_x, '*');
                $centroid_x = substr($centroid_x, 1, -1);
                $list_x = explode(",", $centroid_x);
                $centroid_y = $result['centroid_y'];
                $centroid_y = trim($centroid_y, '*');
                $centroid_y = substr($centroid_y, 1, -1);
                $list_y = explode(",", $centroid_y);
                $replace = "<br><br>";
                for ($x = 0; $x < $clusters; $x++) {
                    $replace .= "Centriod[$x]: x: $list_x[$x] y:$list_y[$x] <br><br>";
                }
                $replace .= "Average time for all process: $avg_time seconds <br><br>";
                $replace .= "Maximum time for process: $max_time seconds <br><br>";
                $htmlContents = file_get_contents("result.html");
                $htmlContents = str_replace("{{TEXT_TO_REPLACE}}",$replace , $htmlContents);
                echo $htmlContents;
            
            }           
            else {
                echo "Wrong File Format Submitted";
            }    
        
        }
        else {
            echo "File not found";
        }
}
else {
    echo "Request is not post!";
}

?>
