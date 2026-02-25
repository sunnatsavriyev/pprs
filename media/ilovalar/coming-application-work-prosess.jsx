import SegmentedButtonGroup from "@/components/ruixen/segmented-button-group";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Sheet,
  SheetClose,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";
import { useChangeComingAplicationMutation, useMEQuery } from "@/services/api";
import { CloudDownload, Send } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
export default function Coming_Application_Details_Work_Pogress({ data }) {
  const [openShet, setOpenShet] = useState(false);
  const { data: me } = useMEQuery();
  const [form, setForm] = useState({
    comment: "",
    status: "qaytarildi",
    ilovalar: null,
    akt_file: null,
  });
  const statusOptions = [
    { label: "Qaytarish", value: "qaytarildi" },
    { label: "Qabul qilish", value: "qabul qilindi" },
    { label: "Bajarish", value: "bajarilgan" },
  ];
  const [ChangeComingApplication, { isLoading: isLoadingComing }] =
    useChangeComingAplicationMutation();
  const isFormComplete = () => form.comment.trim() !== "";
  const submitForm = async () => {
    const fd = new FormData();
    fd.append("comment", form.comment);
    fd.append("ariza", data?.id);
    fd.append("holat", form.status);
    if (form.akt_file) fd.append("akt_file", form.akt_file);
    if (form.ilovalar) fd.append("ilovalar", form.ilovalar);
    await toast.promise(ChangeComingApplication({ body: fd }).unwrap(), {
      loading: "Yuborilmoqda...",
      success: "Yuborildi!",
      error: "Xatolik!",
    });
    setForm({
      comment: "",
      status: "qaytarildi",
      akt_file: null,
      ilovalar: null,
    });
    setOpenShet(false);
  };

  console.log(form);
  const handleDownloadFile = async (url, filename = "file") => {
    try {
      const res = await fetch(url);
      const blob = await res.blob();
      const blobUrl = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = blobUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(blobUrl);
    } catch (err) {
      console.error(err);
    }
  };

  const deleteShetInformation = () => {
    setForm({
      comment: "",
      status: "qaytarildi",
      akt_file: null,
      ilovalar: null,
    });
    setOpenShet(false);
  };
  return (
    <div className="flex flex-col gap-3 w-full mx-auto px-2">
      {/* CHAT MESSAGES */}
      {data?.kelganlar?.map((step) => {
        const d = new Date(step.sana);
        const months = [
          "yanvar",
          "fevral",
          "mart",
          "aprel",
          "may",
          "iyun",
          "iyul",
          "avgust",
          "sentabr",
          "oktabr",
          "noyabr",
          "dekabr",
        ];
        const formattedDate = `${d.toLocaleTimeString("uz-UZ", {
          hour: "2-digit",
          minute: "2-digit",
        })} ${d.getDate()}-${months[d.getMonth()]} ${d.getFullYear()}-yil`;
        const isMe = step.created_by === me?.username;

        return (
          <div
            key={step.id}
            className={`flex ${isMe ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`relative max-w-[75%] p-3 rounded-2xl shadow-md
              ${
                isMe
                  ? "bg-blue-500 text-white rounded-br-none"
                  : "bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-bl-none"
              }`}
            >
              <div className="flex justify-between items-center mb-1 text-[10px]">
                {!isMe && (
                  <span className="font-semibold">{step.created_by}</span>
                )}
                <span
                  className={
                    isMe ? "text-white ml-2" : "dark:text-gray-300 ml-2"
                  }
                >
                  {formattedDate}
                </span>
                {isMe && <span className="font-semibold m ml-2">Men</span>}
              </div>

              {/* COMMENT */}
              <p className="text-sm mb-2 break-words">{step.comment}</p>

              {/* PHOTOS */}
              {step.rasmlar?.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-2">
                  {step.rasmlar.map((url, idx) => (
                    <div key={idx} className="relative group">
                      <img
                        src={url}
                        alt={`img-${idx}`}
                        className="w-24 h-24 object-cover rounded-lg cursor-pointer transition transform "
                        onClick={() => window.open(url, "_blank")}
                      />
                      <button
                        onClick={() =>
                          handleDownloadFile(url, `image-${idx}.jpg`)
                        }
                        className="absolute bottom-1 right-1 p-1 rounded-full shadow opacity-0 group-hover:opacity-100 transition"
                      >
                        <CloudDownload className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
              )}

              {step.bildirgi && (
                <div className="mt-1">
                  <Button
                    size="sm"
                    variant="outline"
                    className="rounded-full flex items-center gap-1 px-3 py-1"
                    onClick={() =>
                      handleDownloadFile(step.bildirgi, "bildirgi.pdf")
                    }
                  >
                    <CloudDownload className="w-4 h-4" /> Bildirgi
                  </Button>
                </div>
              )}

              {step.ilovalar && (
                <div className="mt-1">
                  <Button
                    size="sm"
                    variant="outline"
                    className="rounded-full flex items-center gap-1 px-3 py-1"
                    onClick={() =>
                      handleDownloadFile(step.ilovalar, "ilova.pdf")
                    }
                  >
                    <CloudDownload className="w-4 h-4" /> Ilova
                  </Button>
                </div>
              )}

              {step.akt_file && (
                <div className="mt-1">
                  <Button
                    size="sm"
                    variant="outline"
                    className="rounded-full flex items-center gap-1 px-3 py-1"
                    onClick={() =>
                      handleDownloadFile(step.akt_file, "ilova.pdf")
                    }
                  >
                    <CloudDownload className="w-4 h-4" /> Akt
                  </Button>
                </div>
              )}
            </div>
          </div>
        );
      })}

      {/* ADD NEW STEP */}
      <div className="mt-4 border-t border-border/30 pt-4 space-y-3">
        <div className="flex flex-col justify-center items-start gap-4">
          <SegmentedButtonGroup
            options={statusOptions}
            value={form.status}
            onChange={(value) =>
              setForm((prev) => ({
                ...prev,
                status: value,
              }))
            }
          />
        </div>

        <Textarea
          placeholder="Komment yozing..."
          value={form.comment}
          onChange={(e) => setForm({ ...form, comment: e.target.value })}
          className="w-full h-28 p-2 border border-border rounded-2xl text-sm "
        />

        {form.status == "bajarilgan" ? (
          <Button
            onClick={() => {
              setOpenShet(true);
            }}
            className="flex items-center justify-center gap-2"
          >
            <Send className="w-4 h-4" /> Yuborish
          </Button>
        ) : (
          <Button
            disabled={
              !isFormComplete() ||
              isLoadingComing ||
              data?.status == "bajarilgan"
            }
            onClick={submitForm}
            className="flex items-center justify-center gap-2"
          >
            <Send className="w-4 h-4" /> Yuborish
          </Button>
        )}
      </div>

      {/* add file */}
      <div className="relative flex min-h-screen w-full items-center justify-center">
        <div
          aria-hidden="true"
          className={cn(
            "pointer-events-none -z-10 absolute -top-10 left-1/2 size-full -translate-x-1/2 rounded-full",
            "bg-[radial-gradient(ellipse_at_center,--theme(--color-foreground/.1),transparent_50%)]",
            "blur-[30px]",
          )}
        />

        <Sheet open={openShet}>
          <SheetContent showClose={true}>
            <SheetHeader>
              <SheetTitle>Hujjatlarni yuklash</SheetTitle>
              <SheetDescription>
                Barcha hujjatlarni yuklashga majbursiz
              </SheetDescription>
            </SheetHeader>
            <div className="grid flex-1 auto-rows-min gap-6 px-4">
              <div className="grid gap-3">
                <Label htmlFor="ilovalar">Ilovalar</Label>
                <Input
                  id="ilovalar"
                  type="file"
                  multiple
                  onChange={(e) =>
                    setForm((prev) => ({
                      ...prev,
                      ilovalar: e.target.files[0] || null,
                    }))
                  }
                />
                {form.ilovalar && (
                  <span className="text-xs text-green-600">
                    {form.ilovalar.name}
                  </span>
                )}
              </div>

              <div className="grid gap-3">
                <Label htmlFor="akt_file">Akt fayl</Label>
                <Input
                  id="akt_file"
                  type="file"
                  onChange={(e) =>
                    setForm((prev) => ({
                      ...prev,
                      akt_file: e.target.files[0] || null,
                    }))
                  }
                />
                {form.akt_file && (
                  <span className="text-xs text-green-600">
                    {form.akt_file.name}
                  </span>
                )}
              </div>
            </div>
            <SheetFooter>
              <SheetClose asChild>
                <Button variant="outline" onClick={deleteShetInformation}>
                  Bekor qilish
                </Button>
              </SheetClose>
              <SheetClose asChild>
                <Button
                  disabled={form.ilovalar == null || form.akt_file == null}
                  onClick={submitForm}
                >
                  Yuborish
                </Button>
              </SheetClose>
            </SheetFooter>
          </SheetContent>
        </Sheet>

        {/* <NavigationMenuDemo /> */}
      </div>
    </div>
  );
}
