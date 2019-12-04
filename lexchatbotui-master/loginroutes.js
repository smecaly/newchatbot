var AWS = require("aws-sdk");

AWS.config.update({region:'us-east-1'});
var dynamodb = new AWS.DynamoDB({ 'region': 'us-east-1'});
var docClient = new AWS.DynamoDB.DocumentClient({"service": dynamodb});

exports.login = function(req,res){
  var uname= req.body.uname;
  var pwd = req.body.psw;
  var params = {
    TableName : "userdetails",
    KeyConditionExpression: "#usr = :user",
    ExpressionAttributeNames:{
        "#usr": "username"
    },
    ExpressionAttributeValues: {
        ":user": uname
    }
};
docClient.query(params, function(err, data) {
    if (err) {
	console.error("Unable to query. Error:", JSON.stringify(err, null, 2));

    } 
	else {
        if (data.Items.length > 0){
        data.Items.forEach(function(item) {
            if (item.password == pwd){
             //   res.sendFile("/home/ec2-user/front-end/aws-lex-web-ui/src/website/parent.html");
		res.sendFile( __dirname + "/" + "/src/website/parent.html" );
           }
            else{
                res.send({
          "code":204,
          "error":"Email and password does not match"
           });
           }
        });
        }
        else{
        
		  res.send("Invalid User..");
		  
		  }
		  }
    });
}
