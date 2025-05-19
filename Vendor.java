import java.io.*;
import java.net.*;
import java.nio.file.*;
import java.util.*;

public class Vendor {
    private static final int PORT = 8080;
    private static final String STATIC_DIR = "static";
    private static final String[] IMAGE_FILES = {
        "plot_itemwise_increase.png",
        "plot_vendor_trust.png",
        "plot_anomalies.png",
        "decision_tree_structure.png"
    };

    public static void main(String[] args) {
        try {
            // Run the Python analysis
            runPythonAnalysis();

            // Start the web server
            startWebServer();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private static void runPythonAnalysis() throws IOException, InterruptedException {
        System.out.println("Running vendor analysis...");
        ProcessBuilder pb = new ProcessBuilder("python", "app.py");
        pb.redirectErrorStream(true);
        
        Process process = pb.start();
        
        // Print Python output
        try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(process.getInputStream()))) {
            String line;
            while ((line = reader.readLine()) != null) {
                System.out.println("[PYTHON] " + line);
            }
        }
        
        int exitCode = process.waitFor();
        if (exitCode != 0) {
            throw new RuntimeException("Python script failed with exit code " + exitCode);
        }
        System.out.println("Analysis completed successfully!");
    }

    private static void startWebServer() throws IOException {
        try (ServerSocket serverSocket = new ServerSocket(PORT)) {
            System.out.println("Server started at http://localhost:" + PORT);
            System.out.println("Displaying visualizations...");

            while (true) {
                try (Socket clientSocket = serverSocket.accept();
                     PrintWriter out = new PrintWriter(clientSocket.getOutputStream(), true);
                     BufferedReader in = new BufferedReader(
                         new InputStreamReader(clientSocket.getInputStream()))) {

                    // Read HTTP request
                    while (!in.readLine().isEmpty()); // Skip headers

                    // Generate HTML response
                    String html = generateHtmlResponse();
                    
                    // Send response
                    out.println("HTTP/1.1 200 OK");
                    out.println("Content-Type: text/html");
                    out.println("Content-Length: " + html.getBytes().length);
                    out.println();
                    out.println(html);
                }
            }
        }
    }

    private static String generateHtmlResponse() {
        StringBuilder html = new StringBuilder();
        html.append("<!DOCTYPE html><html><head>");
        html.append("<title>Vendor Analysis Visualizations</title>");
        html.append("<style>");
        html.append("body { font-family: Arial, sans-serif; margin: 20px; }");
        html.append("h1 { color: #2c3e50; }");
        html.append(".image-container { margin-bottom: 30px; border: 1px solid #ddd; padding: 10px; }");
        html.append("img { max-width: 100%; height: auto; display: block; margin: 0 auto; }");
        html.append(".caption { text-align: center; margin-top: 10px; font-weight: bold; }");
        html.append("</style>");
        html.append("</head><body>");
        html.append("<h1>Vendor Analysis Visualizations</h1>");

        // Add each image with caption
        Map<String, String> imageCaptions = new LinkedHashMap<>();
        imageCaptions.put("plot_itemwise_increase.png", "Item-wise Price Increase (%)");
        imageCaptions.put("plot_vendor_trust.png", "Vendor Profit Margins with Trust Status");
        imageCaptions.put("plot_anomalies.png", "Anomaly Detection in Vendor Profit Margins");
        imageCaptions.put("decision_tree_structure.png", "Decision Tree for Trust Classification");

        for (Map.Entry<String, String> entry : imageCaptions.entrySet()) {
            String filename = entry.getKey();
            Path imagePath = Paths.get(STATIC_DIR, filename);
            
            if (Files.exists(imagePath)) {
                html.append("<div class='image-container'>");
                html.append("<img src='data:image/png;base64,")
                    .append(getBase64Image(imagePath))
                    .append("' alt='").append(entry.getValue()).append("'>");
                html.append("<div class='caption'>").append(entry.getValue()).append("</div>");
                html.append("</div>");
            }
        }

        html.append("</body></html>");
        return html.toString();
    }

    private static String getBase64Image(Path imagePath) {
        try {
            byte[] imageBytes = Files.readAllBytes(imagePath);
            return Base64.getEncoder().encodeToString(imageBytes);
        } catch (IOException e) {
            System.err.println("Error reading image file: " + imagePath);
            return "";
        }
    }
}