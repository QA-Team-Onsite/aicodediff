package org.example.diffmethod.controller;
import com.github.javaparser.*;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.body.ClassOrInterfaceDeclaration;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;

import java.io.File;
import java.io.IOException;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.List;
import java.util.Optional;

import static jdk.nashorn.internal.runtime.regexp.joni.Config.log;

@RestController
public class DiffMethod {
    @PostMapping("/codediff/diffmethod")
    public ResponseEntity<DiffMethodResponse> diffmethod(@RequestBody DiffMethodDict diffMethodDict) throws IOException {
        // 设置要解析的 Java 文件路径
//        log.info("name:{}",diffMethodDict.getMethodName());
//        log.info("age:{}",diffMethodDict.getMethodPath());

        //String filePath = "D:\\codediff\\dw-growth-center\\dw-market-center\\src\\main\\java\\com\\easyhome\\marketcenter\\serviceimpl\\honeycomb\\DistributorManagementServiceImpl.java"; // 替换为你要解析的文件路径
        System.out.println("getMethodPath: " + diffMethodDict.getMethodPath());

        File file = new File(diffMethodDict.getMethodPath());

        // 创建 JavaParser 实例并解析 Java 文件
        JavaParser parser = new JavaParser();
        ParseResult<CompilationUnit> result = parser.parse(file);

        // 创建返回结构
        DiffMethodResponse response = new DiffMethodResponse();
        response.setCode(200);
        response.setMethods(new HashMap<>());
        // 检查解析是否成功
        if (result.isSuccessful()) {
            Optional<CompilationUnit> optionalCu = result.getResult();
            if (optionalCu.isPresent()) {
                CompilationUnit cu = optionalCu.get();

                // 查找所有类，并打印类名和其中的方法
                List<ClassOrInterfaceDeclaration> classes = cu.findAll(ClassOrInterfaceDeclaration.class);
                for (ClassOrInterfaceDeclaration clazz : classes) {
                    System.out.println("Class: " + clazz.getName());
                    response.setClazz(clazz.getNameAsString());
                    // 查找类中的所有方法
                    List<MethodDeclaration> methods = clazz.getMethods();
                    for (MethodDeclaration method : methods) {
                        MethodInfo methodInfo = new MethodInfo();

                        // 方法体


                        method.getRange().ifPresent(range -> {
                            int beginLine = range.begin.line;
                            int endLine = range.end.line;

                            String sourceCode = null;
                            try {
                                sourceCode = new String(java.nio.file.Files.readAllBytes(file.toPath()));
                            } catch (IOException e) {
                                throw new RuntimeException(e);
                            }

                            String[] lines = sourceCode.split("\n");
                            StringBuilder rawCode = new StringBuilder();
                            for (int i = beginLine - 1; i < endLine; i++) {
                                if (i >= 0 && i < lines.length) {
                                    rawCode.append(lines[i]).append("\n");



                                }
                            }

                            methodInfo.setMethodCode(rawCode.toString());
                            methodInfo.setBeginLine(beginLine);
                            methodInfo.setEndLine(endLine);
                        });
                        // 行号
                        method.getRange().ifPresent(range -> {
                            methodInfo.setBeginLine(range.begin.line);
                            methodInfo.setEndLine(range.end.line);
                        });

                        response.getMethods().put(method.getNameAsString(), methodInfo);

                        System.out.println("  Method: " + method.getName());
                        System.out.println(methodInfo.getMethodCode());

//                        response.getMethods().put(method.getNameAsString(), method.toString());
//
//                        System.out.println("  Method: " + method.getName());
//                        System.out.println(method.toString());
                    }
                }
            } else {
                System.out.println("CompilationUnit is not present.");
                response.setCode(500); // 如果解析失败，返回错误代码

            }
        } else {
            System.out.println("Java file parsing failed.");
            response.setCode(500); // 如果解析失败，返回错误代码

        }
        return ResponseEntity.ok(response); // 返回构建的响应对象

    }
}
