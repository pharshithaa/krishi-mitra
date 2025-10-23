
import React, { useState } from "react";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Upload, ImagePlus, CheckCircle, Info } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useToast } from "@/components/ui/use-toast";

interface DetectionResult {
  disease: string;
  probability: number;
  description: string;
  treatment: string[];
  prevention: string[];
}

const mockDetectionResult: DetectionResult = {
  disease: "Late Blight",
  probability: 92,
  description: "Late blight is a plant disease caused by the fungus-like oomycete pathogen Phytophthora infestans. It primarily affects potatoes and tomatoes, causing significant crop damage.",
  treatment: [
    "Apply copper-based fungicides as directed",
    "Remove and destroy infected plant parts",
    "Improve air circulation around plants",
    "Use targeted biological controls"
  ],
  prevention: [
    "Plant resistant varieties",
    "Ensure proper spacing between plants",
    "Avoid overhead irrigation",
    "Practice crop rotation",
    "Keep the garden clean of plant debris"
  ]
};

const DiseaseDetection: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<DetectionResult | null>(null);
  const { toast } = useToast();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      
      // Create image preview
      const reader = new FileReader();
      reader.onload = (event) => {
        setImagePreview(event.target?.result as string);
      };
      reader.readAsDataURL(file);
      
      // Reset previous results
      setResult(null);
    }
  };

  const handleAnalyze = () => {
    if (!selectedFile) {
      toast({
        title: "No image selected",
        description: "Please upload an image to analyze",
        variant: "destructive",
      });
      return;
    }

    setIsAnalyzing(true);
    
    // Simulate API call with timeout
    setTimeout(() => {
      setResult(mockDetectionResult);
      setIsAnalyzing(false);
      
      toast({
        title: "Analysis Complete",
        description: "Disease detection results are ready",
      });
    }, 2000);
  };

  const resetForm = () => {
    setSelectedFile(null);
    setImagePreview(null);
    setResult(null);
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <Card>
        <CardHeader>
          <CardTitle>Plant Disease Detection</CardTitle>
          <CardDescription>
            Upload a clear image of the affected plant for analysis
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="grid w-full items-center gap-1.5">
              <Label htmlFor="plant-image">Plant Image</Label>
              <div className="flex items-center gap-2">
                <Input
                  id="plant-image"
                  type="file"
                  accept="image/*"
                  onChange={handleFileChange}
                  className="hidden"
                />
                <div className="grid gap-1.5 w-full">
                  <Label
                    htmlFor="plant-image"
                    className="cursor-pointer flex items-center justify-center w-full border-2 border-dashed border-gray-300 rounded-md h-32 hover:border-primary transition-colors"
                  >
                    {imagePreview ? (
                      <div className="w-full h-full relative">
                        <img
                          src={imagePreview}
                          alt="Preview"
                          className="w-full h-full object-contain"
                        />
                      </div>
                    ) : (
                      <div className="flex flex-col items-center text-gray-500">
                        <ImagePlus className="w-10 h-10 mb-2" />
                        <span>Click to upload image</span>
                      </div>
                    )}
                  </Label>
                  {selectedFile && (
                    <p className="text-sm text-gray-500">
                      {selectedFile.name}
                    </p>
                  )}
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <Label>Tips for better results:</Label>
              <ul className="text-sm text-gray-500 list-disc pl-5 space-y-1">
                <li>Ensure good lighting and clear focus</li>
                <li>Take close-up shots of affected areas</li>
                <li>Include both affected and healthy parts for comparison</li>
                <li>Avoid shadows or glare in the image</li>
              </ul>
            </div>
          </div>
        </CardContent>
        <CardFooter className="flex justify-between">
          <Button variant="outline" onClick={resetForm} disabled={isAnalyzing}>
            Reset
          </Button>
          <Button onClick={handleAnalyze} disabled={!selectedFile || isAnalyzing}>
            {isAnalyzing ? (
              <>Analyzing...</>
            ) : (
              <>
                <Upload className="mr-2 h-4 w-4" /> Analyze Image
              </>
            )}
          </Button>
        </CardFooter>
      </Card>

      <Card className={result ? "" : "flex items-center justify-center"}>
        {result ? (
          <>
            <CardHeader>
              <CardTitle className="flex items-center">
                <span className="text-agro-red mr-2">
                  {result.disease}
                </span>
                <span className="text-sm font-normal text-gray-500">
                  ({result.probability}% confidence)
                </span>
              </CardTitle>
              <CardDescription>{result.description}</CardDescription>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="treatment">
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="treatment">Treatment</TabsTrigger>
                  <TabsTrigger value="prevention">Prevention</TabsTrigger>
                </TabsList>
                <TabsContent value="treatment" className="pt-4">
                  <div className="space-y-4">
                    <div className="bg-amber-50 p-3 rounded-md">
                      <div className="flex items-start">
                        <Info className="w-5 h-5 text-amber-500 mr-2 mt-0.5" />
                        <p className="text-sm">
                          Apply treatments promptly for best results. Always follow
                          product instructions and consider organic options when possible.
                        </p>
                      </div>
                    </div>
                    <ul className="space-y-2">
                      {result.treatment.map((item, index) => (
                        <li key={index} className="flex items-start">
                          <CheckCircle className="w-5 h-5 text-green-500 mr-2 mt-0.5 shrink-0" />
                          <span>{item}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </TabsContent>
                <TabsContent value="prevention" className="pt-4">
                  <ul className="space-y-2">
                    {result.prevention.map((item, index) => (
                      <li key={index} className="flex items-start">
                        <CheckCircle className="w-5 h-5 text-blue-500 mr-2 mt-0.5 shrink-0" />
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </TabsContent>
              </Tabs>
            </CardContent>
          </>
        ) : (
          <div className="text-center p-6">
            <div className="rounded-full bg-gray-100 w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <Upload className="h-8 w-8 text-gray-400" />
            </div>
            <h3 className="text-lg font-medium text-gray-700 mb-2">
              No Analysis Results Yet
            </h3>
            <p className="text-gray-500 text-sm">
              Upload an image and click "Analyze" to detect plant diseases
            </p>
          </div>
        )}
      </Card>
    </div>
  );
};

export default DiseaseDetection;
